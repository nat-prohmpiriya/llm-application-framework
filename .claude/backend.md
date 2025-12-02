# Backend Instructions (FastAPI + Python)

## Tech Stack
- FastAPI + Python 3.12+
- SQLAlchemy async + PostgreSQL
- Pydantic v2
- JWT (python-jose) + bcrypt
- OpenTelemetry + Jaeger
- uv (package manager)

## Architecture

```
Request → Middleware → Routes → Services → Models/Providers → Response
              ↓           ↓          ↓
         RequestContext  Schemas   Database
              ↓
          trace_id
```

### Layer Rules
1. **Routes**: HTTP only, validate input, call services
2. **Services**: Business logic, DB queries, no HTTP knowledge
3. **Models**: SQLAlchemy ORM, no business logic
4. **Schemas**: Pydantic request/response validation
5. **Providers**: External API clients (LiteLLM, ChromaDB)

## Project Structure

```
app/
├── main.py              # Entrypoint
├── config.py            # Settings
├── schemas/             # Pydantic models
├── routes/              # API endpoints
├── services/            # Business logic
├── models/              # SQLAlchemy ORM
├── providers/           # External clients
├── middleware/          # Request middleware
└── core/                # Shared utilities
```

## Python Style

### Type Hints (Required)
```python
# ✅ Good
async def get_user(user_id: int) -> User | None:
    ...

# ❌ Bad
async def get_user(user_id):
    ...
```

### Modern Syntax
```python
# ✅ Good
name: str | None = None

# ❌ Bad
name: Optional[str] = None
```

### Pydantic v2
```python
from pydantic import BaseModel, ConfigDict

class UserResponse(BaseModel):
    id: int
    email: str
    model_config = ConfigDict(from_attributes=True)
```

## API Response Format

**All responses MUST use BaseResponse[T]:**

```python
from app.schemas.base import BaseResponse
from app.core.context import get_context

@router.get("/{user_id}")
async def get_user(user_id: int) -> BaseResponse[UserResponse]:
    ctx = get_context()
    user = await user_service.get_user(db, user_id)
    return BaseResponse(
        trace_id=ctx.trace_id,
        data=UserResponse.model_validate(user),
    )
```

## Streaming (SSE)

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

## Commands

```bash
uv sync                              # Install
uv run uvicorn app.main:app --reload # Dev
uv run alembic upgrade head          # Migrate
uv run pytest                        # Test
uv run ruff check . --fix            # Lint
```
