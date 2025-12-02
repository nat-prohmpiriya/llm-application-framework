# API Routes Instructions

## Route Pattern

```python
from fastapi import APIRouter, Depends
from app.core.dependencies import get_db, get_current_user
from app.core.context import get_context
from app.schemas.base import BaseResponse

router = APIRouter(prefix="/users", tags=["users"])

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

## Route Responsibilities

Routes should ONLY:
1. Define HTTP endpoint
2. Validate request data (via Pydantic)
3. Call service function
4. Return wrapped response

Routes should NOT:
- Contain business logic
- Make direct DB queries
- Handle complex error conditions

## Streaming Responses

```python
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

## HTTP Status Codes

```python
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(...):
    ...

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(...):
    ...
```
