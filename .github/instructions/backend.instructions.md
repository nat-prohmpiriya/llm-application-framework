---
applyTo: "backend/**"
---

# Backend Instructions (FastAPI + Python)

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| Language | Python 3.12+ |
| Package Manager | uv |
| Database | PostgreSQL + SQLAlchemy (async) |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | JWT (python-jose) + bcrypt |
| Linter/Formatter | Ruff |
| Tracing | OpenTelemetry + Jaeger |

## Architecture Rules

1. **Routes**: Only handle HTTP, validate input, call services
2. **Services**: Business logic, DB queries, no HTTP knowledge
3. **Models**: Database tables only, no business logic
4. **Schemas**: Request/Response validation, separate from Models
5. **Providers**: External API clients (stateless)
6. **Core**: Shared utilities used across all layers

### Data Flow

```
Request → Middleware → Routes → Services → Models/Providers → Response
              ↓           ↓          ↓
         RequestContext  Schemas   Database
              ↓
          trace_id
```

## Project Structure

```
app/
├── main.py              # FastAPI entrypoint
├── config.py            # Environment settings
├── schemas/             # Pydantic schemas
├── routes/              # API endpoints
├── services/            # Business logic
├── models/              # SQLAlchemy ORM
├── providers/           # External integrations
├── middleware/          # Request middleware
└── core/                # Shared utilities
```

## Python Style Guide

### Type Hints

Always use type hints:

```python
# ✅ Good
async def get_user(user_id: int) -> User | None:
    ...

# ❌ Bad
async def get_user(user_id):
    ...
```

### Modern Type Syntax

Use Python 3.10+ syntax:

```python
# ✅ Good
def process(name: str | None = None) -> dict[str, Any]:
    ...

# ❌ Bad (legacy)
def process(name: Optional[str] = None) -> Dict[str, Any]:
    ...
```

### Pydantic v2

Always enable ORM mode for response schemas:

```python
from pydantic import BaseModel, ConfigDict

class UserResponse(BaseModel):
    id: int
    email: str
    username: str

    # Pydantic v2 syntax
    model_config = ConfigDict(from_attributes=True)
```

### Schema Naming Convention

| Suffix | Use For | Example |
|--------|---------|---------|
| `*Create` | API Request (POST) | `UserCreate` |
| `*Update` | API Request (PUT/PATCH) | `UserUpdate` |
| `*Response` | API Response | `UserResponse` |
| `*Input` | Internal service input | `CreateUserInput` |

## API Response Format

All responses must include `trace_id`:

```python
from app.schemas.base import BaseResponse
from app.core.context import get_context

@router.get("/users/me")
async def get_me(current_user: User = Depends(get_current_user)) -> BaseResponse[UserResponse]:
    ctx = get_context()
    return BaseResponse(
        trace_id=ctx.trace_id,
        data=UserResponse.model_validate(current_user),
    )
```

Response format:
```json
{
  "trace_id": "abc123...",
  "data": { ... }
}
```

## Streaming Responses (SSE)

For LLM chat endpoints:
- Use `StreamingResponse` instead of `BaseResponse`
- Include `trace_id` in `X-Trace-Id` header

```python
from fastapi.responses import StreamingResponse

@router.post("/chat/stream")
async def chat_stream(data: ChatRequest):
    ctx = get_context()

    async def event_generator():
        async for chunk in llm_service.chat_stream(data.message):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"X-Trace-Id": ctx.trace_id}
    )
```

## Tracing with @traced Decorator

```python
from app.core.telemetry import traced

@traced()
async def create_order(db: AsyncSession, data: OrderCreate) -> Order:
    # Auto tracks: input, output, timing
    ...

@traced(skip_input=True)  # For sensitive data
async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    ...
```

## Async/Await

Use `async/await` for all DB and HTTP operations:

```python
# ✅ Good
async def get_users(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User))
    return result.scalars().all()

# ❌ Bad (blocking)
def get_users(db: Session) -> list[User]:
    return db.query(User).all()
```

## Dependency Injection

```python
from fastapi import Depends
from app.core.dependencies import get_db, get_current_user

@router.get("/me")
async def get_me(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    return current_user
```

## Import Order (PEP8)

```python
# 1. Standard library
import os
from datetime import datetime

# 2. Third-party packages
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

# 3. Local imports
from app.config import settings
from app.models.user import User
```

## Commands

```bash
cd backend
uv sync                              # Install dependencies
uv run uvicorn app.main:app --reload # Run dev server
uv run alembic upgrade head          # Run migrations
uv run pytest                        # Run tests
uv run ruff check . --fix            # Lint & fix
uv run ruff format .                 # Format code
```
