"""Chat API routes."""

import json
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.core.context import get_context
from app.core.dependencies import get_current_user
from app.models.user import User
from app.providers.llm import ChatMessage as LLMChatMessage
from app.providers.llm import llm_client
from app.schemas.base import BaseResponse
from app.schemas.chat import ChatMessage, ChatRequest, ChatResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
async def chat(
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
) -> BaseResponse[ChatResponse]:
    """
    Send a chat message and get a response (non-streaming).

    Requires authentication.
    """
    ctx = get_context()
    ctx.user_id = current_user.id
    ctx.set_data({
        "action": "chat",
        "model": data.model or llm_client.default_model,
        "message_length": len(data.message),
    })

    try:
        # Build messages list (simple for now, later add conversation history)
        messages = [
            LLMChatMessage(role="user", content=data.message),
        ]

        # Call LLM
        response = await llm_client.chat_completion(
            messages=messages,
            model=data.model,
            temperature=data.temperature,
        )

        # Build response
        chat_response = ChatResponse(
            message=ChatMessage(
                role=response.role,
                content=response.content,
                created_at=datetime.utcnow(),
            ),
            model=response.model,
            usage=response.usage,
            conversation_id=data.conversation_id,
        )

        return BaseResponse(
            trace_id=ctx.trace_id,
            data=chat_response,
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.post("/stream")
async def chat_stream(
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Send a chat message and get a streaming response (SSE).

    Requires authentication.
    Returns Server-Sent Events with X-Trace-Id header.
    """
    ctx = get_context()
    ctx.user_id = current_user.id
    ctx.set_data({
        "action": "chat_stream",
        "model": data.model or llm_client.default_model,
        "message_length": len(data.message),
    })

    async def event_generator():
        try:
            # Build messages list
            messages = [
                LLMChatMessage(role="user", content=data.message),
            ]

            # Stream response
            async for chunk in llm_client.chat_completion_stream(
                messages=messages,
                model=data.model,
                temperature=data.temperature,
            ):
                # SSE format: data: {"content": "...", "done": false}
                event_data = json.dumps({"content": chunk, "done": False})
                yield f"data: {event_data}\n\n"

            # Send done signal
            yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"

        except Exception as e:
            logger.error(f"Chat stream error: {e}")
            error_data = json.dumps({"error": str(e), "done": True})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "X-Trace-Id": ctx.trace_id,
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
