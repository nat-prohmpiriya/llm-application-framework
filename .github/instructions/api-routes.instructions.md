---
applyTo: "backend/app/routes/**"
---

# API Route Instructions

## Route File Structure

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.core.context import get_context
from app.schemas.base import BaseResponse
from app.schemas.user import UserCreate, UserResponse
from app.services import user_service
from app.models import User

router = APIRouter(prefix="/users", tags=["users"])
```

## Response Wrapper Pattern

**ALL responses MUST use `BaseResponse[T]`:**

```python
from app.schemas.base import BaseResponse
from app.core.context import get_context

@router.get("/{user_id}")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BaseResponse[UserResponse]:
    ctx = get_context()
    user = await user_service.get_user(db, user_id)
    return BaseResponse(
        trace_id=ctx.trace_id,
        data=UserResponse.model_validate(user),
    )
```

## Streaming Responses (SSE)

For LLM/chat endpoints, use StreamingResponse with X-Trace-Id header:

```python
from fastapi.responses import StreamingResponse

@router.post("/stream")
async def chat_stream(
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
):
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

## Route Responsibilities

Routes should ONLY:
1. Define HTTP endpoint (method, path)
2. Parse and validate request data (via Pydantic schemas)
3. Call appropriate service function
4. Return wrapped response

Routes should NOT:
- Contain business logic
- Make direct DB queries
- Handle complex error conditions

## Dependency Injection

```python
from app.core.dependencies import get_db, get_current_user, get_current_active_user

# Public endpoint (no auth)
@router.get("/public")
async def public_endpoint(db: AsyncSession = Depends(get_db)):
    ...

# Protected endpoint (requires valid JWT)
@router.get("/protected")
async def protected_endpoint(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ...
```

## HTTP Status Codes

```python
from fastapi import status

# 201 for creation
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(...) -> BaseResponse[UserResponse]:
    ...

# 204 for deletion (no content)
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(...):
    ...
```

## Error Handling

Let services raise exceptions, use global exception handlers:

```python
# In service (NOT in route)
from app.core.exceptions import NotFoundError

async def get_user(db: AsyncSession, user_id: int) -> User:
    user = await db.get(User, user_id)
    if not user:
        raise NotFoundError("User", user_id)
    return user

# Route just calls service - exception handler converts to 404
@router.get("/{user_id}")
async def get_user_endpoint(user_id: int, db: AsyncSession = Depends(get_db)):
    return await user_service.get_user(db, user_id)
```
