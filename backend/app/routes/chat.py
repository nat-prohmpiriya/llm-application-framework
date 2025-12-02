"""Chat API routes."""

import json
import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import get_context
from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.providers.llm import ChatMessage as LLMChatMessage
from app.providers.llm import llm_client
from app.schemas.base import BaseResponse
from app.schemas.chat import ChatMessage, ChatRequest, ChatResponse, UsageInfo
from app.services import conversation as conversation_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


class ModelInfo(BaseModel):
    """Model information."""
    id: str
    name: str
    provider: str
    description: str | None = None
    context_window: int | None = None
    input_price: float | None = None  # per million tokens
    output_price: float | None = None  # per million tokens
    tier: str | None = None  # "free", "pro", "enterprise"
    model_page_url: str | None = None
    pricing_url: str | None = None
    terms_url: str | None = None
    privacy_url: str | None = None
    website_url: str | None = None


class ModelsResponse(BaseModel):
    """Models list response."""
    models: list[ModelInfo]


# Available models configuration - must match litellm-config.yaml
AVAILABLE_MODELS = [
    # Google Gemini Models
    ModelInfo(
        id="gemini-2.0-flash",
        name="Gemini 2.0 Flash",
        provider="google",
        description="Fast and efficient model for most tasks with multimodal capabilities",
        context_window=1000000,
        input_price=0.075,
        output_price=0.30,
        tier="free",
        model_page_url="https://ai.google.dev/gemini-api/docs/models#gemini-2.0-flash",
        pricing_url="https://ai.google.dev/pricing",
        terms_url="https://policies.google.com/terms",
        privacy_url="https://policies.google.com/privacy",
        website_url="https://ai.google.dev",
    ),
    ModelInfo(
        id="gemini-1.5-pro",
        name="Gemini 1.5 Pro",
        provider="google",
        description="Most capable Gemini model for complex reasoning and analysis",
        context_window=2000000,
        input_price=1.25,
        output_price=5.00,
        tier="pro",
        model_page_url="https://ai.google.dev/gemini-api/docs/models#gemini-1.5-pro",
        pricing_url="https://ai.google.dev/pricing",
        terms_url="https://policies.google.com/terms",
        privacy_url="https://policies.google.com/privacy",
        website_url="https://ai.google.dev",
    ),
    ModelInfo(
        id="gemini-1.5-flash",
        name="Gemini 1.5 Flash",
        provider="google",
        description="Balanced speed and capability for everyday tasks",
        context_window=1000000,
        input_price=0.075,
        output_price=0.30,
        tier="free",
        model_page_url="https://ai.google.dev/gemini-api/docs/models#gemini-1.5-flash",
        pricing_url="https://ai.google.dev/pricing",
        terms_url="https://policies.google.com/terms",
        privacy_url="https://policies.google.com/privacy",
        website_url="https://ai.google.dev",
    ),
    # Groq Models
    ModelInfo(
        id="llama-3.3-70b",
        name="Llama 3.3 70B",
        provider="groq",
        description="Powerful open-source model via Groq with fast inference",
        context_window=128000,
        input_price=0.59,
        output_price=0.79,
        tier="pro",
        model_page_url="https://console.groq.com/docs/models",
        pricing_url="https://groq.com/pricing",
        terms_url="https://groq.com/terms-of-use",
        privacy_url="https://groq.com/privacy-policy",
        website_url="https://groq.com",
    ),
    ModelInfo(
        id="llama-3.1-8b",
        name="Llama 3.1 8B",
        provider="groq",
        description="Fast lightweight model via Groq for simple tasks",
        context_window=128000,
        input_price=0.05,
        output_price=0.08,
        tier="free",
        model_page_url="https://console.groq.com/docs/models",
        pricing_url="https://groq.com/pricing",
        terms_url="https://groq.com/terms-of-use",
        privacy_url="https://groq.com/privacy-policy",
        website_url="https://groq.com",
    ),
    ModelInfo(
        id="mixtral-8x7b",
        name="Mixtral 8x7B",
        provider="groq",
        description="Mixture of experts model via Groq with excellent performance",
        context_window=32768,
        input_price=0.24,
        output_price=0.24,
        tier="free",
        model_page_url="https://console.groq.com/docs/models",
        pricing_url="https://groq.com/pricing",
        terms_url="https://groq.com/terms-of-use",
        privacy_url="https://groq.com/privacy-policy",
        website_url="https://groq.com",
    ),
]


@router.get("/models")
async def get_models(
    current_user: User = Depends(get_current_user),
) -> BaseResponse[ModelsResponse]:
    """
    Get available models for chat.

    Requires authentication.
    """
    ctx = get_context()
    ctx.user_id = current_user.id

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=ModelsResponse(models=AVAILABLE_MODELS),
    )


async def get_or_create_conversation(
    db: AsyncSession,
    user_id: uuid.UUID,
    conversation_id: uuid.UUID | None,
) -> uuid.UUID:
    """Get existing conversation or create a new one."""
    if conversation_id:
        # Verify the conversation exists and belongs to user
        await conversation_service.get_conversation_simple(
            db=db,
            conversation_id=conversation_id,
            user_id=user_id,
        )
        return conversation_id
    else:
        # Create a new conversation
        conversation = await conversation_service.create_conversation(
            db=db,
            user_id=user_id,
            title=None,  # Title will be set later or auto-generated
        )
        return conversation.id


async def build_messages_from_history(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    user_id: uuid.UUID,
    new_message: str,
) -> list[LLMChatMessage]:
    """Build message list from conversation history plus new message."""
    messages: list[LLMChatMessage] = []

    # Get existing messages from conversation
    history = await conversation_service.get_conversation_messages(
        db=db,
        conversation_id=conversation_id,
        user_id=user_id,
    )

    # Add history messages
    for msg in history:
        messages.append(
            LLMChatMessage(role=msg.role.value, content=msg.content)
        )

    # Add new user message
    messages.append(LLMChatMessage(role="user", content=new_message))

    return messages


@router.post("")
async def chat(
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[ChatResponse]:
    """
    Send a chat message and get a response (non-streaming).

    If conversation_id is not provided, a new conversation will be created.
    Messages are saved to the database.

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
        # Get or create conversation
        conversation_id = await get_or_create_conversation(
            db=db,
            user_id=current_user.id,
            conversation_id=data.conversation_id,
        )

        # Save user message to DB
        await conversation_service.add_message(
            db=db,
            conversation_id=conversation_id,
            role="user",
            content=data.message,
        )

        # Build messages list from history
        messages = await build_messages_from_history(
            db=db,
            conversation_id=conversation_id,
            user_id=current_user.id,
            new_message=data.message,
        )

        # Remove the last message since we already added it
        messages = messages[:-1]
        messages.append(LLMChatMessage(role="user", content=data.message))

        # Call LLM with user_id for usage tracking
        response = await llm_client.chat_completion(
            messages=messages,
            model=data.model,
            temperature=data.temperature,
            max_tokens=data.max_tokens,
            top_p=data.top_p,
            frequency_penalty=data.frequency_penalty,
            presence_penalty=data.presence_penalty,
            user=str(current_user.id),
        )

        # Save assistant message to DB
        tokens_used = response.usage.get("total_tokens") if response.usage else None
        await conversation_service.add_message(
            db=db,
            conversation_id=conversation_id,
            role="assistant",
            content=response.content,
            tokens_used=tokens_used,
        )

        # Build response
        usage_info = UsageInfo(**response.usage) if response.usage else None
        chat_response = ChatResponse(
            message=ChatMessage(
                role=response.role,
                content=response.content,
                created_at=datetime.utcnow(),
            ),
            model=response.model,
            usage=usage_info,
            conversation_id=conversation_id,
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
    db: AsyncSession = Depends(get_db),
):
    """
    Send a chat message and get a streaming response (SSE).

    If conversation_id is not provided, a new conversation will be created.
    Messages are saved to the database.

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

    # Get or create conversation before streaming starts
    conversation_id = await get_or_create_conversation(
        db=db,
        user_id=current_user.id,
        conversation_id=data.conversation_id,
    )

    # Save user message to DB
    await conversation_service.add_message(
        db=db,
        conversation_id=conversation_id,
        role="user",
        content=data.message,
    )

    # Build messages list from history
    messages = await build_messages_from_history(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id,
        new_message=data.message,
    )

    # Remove duplicate user message
    messages = messages[:-1]
    messages.append(LLMChatMessage(role="user", content=data.message))

    # Get user_id for closure
    user_id_str = str(current_user.id)

    async def event_generator():
        full_response = ""
        try:
            # Stream response with user_id for usage tracking
            async for chunk in llm_client.chat_completion_stream(
                messages=messages,
                model=data.model,
                temperature=data.temperature,
                max_tokens=data.max_tokens,
                top_p=data.top_p,
                frequency_penalty=data.frequency_penalty,
                presence_penalty=data.presence_penalty,
                user=user_id_str,
            ):
                full_response += chunk
                # SSE format: data: {"content": "...", "done": false}
                event_data = json.dumps({
                    "content": chunk,
                    "done": False,
                    "conversation_id": str(conversation_id),
                })
                yield f"data: {event_data}\n\n"

            # Save assistant message after streaming completes
            # Note: We can't get token count from streaming response
            await conversation_service.add_message(
                db=db,
                conversation_id=conversation_id,
                role="assistant",
                content=full_response,
                tokens_used=None,
            )

            # Send done signal
            yield f"data: {json.dumps({'content': '', 'done': True, 'conversation_id': str(conversation_id)})}\n\n"

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
