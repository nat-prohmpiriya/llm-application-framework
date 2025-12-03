from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import get_context
from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import ConflictError
from app.models.agent import Agent
from app.models.conversation import Conversation
from app.models.document import Document
from app.models.message import Message
from app.models.user import User
from app.schemas.base import BaseResponse, MessageResponse
from app.schemas.stats import UserStatsResponse
from app.schemas.user import (
    ChangePasswordRequest,
    DeleteAccountRequest,
    UserProfileResponse,
    UserUpdate,
)
from app.services.auth import change_password, delete_account

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("")
async def get_profile(
    current_user: User = Depends(get_current_user),
) -> BaseResponse[UserProfileResponse]:
    """Get current user's profile."""
    ctx = get_context()
    return BaseResponse(
        trace_id=ctx.trace_id,
        data=UserProfileResponse.model_validate(current_user),
    )


@router.put("")
async def update_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[UserProfileResponse]:
    """Update current user's profile."""
    ctx = get_context()

    # Check username uniqueness if provided
    if data.username and data.username != current_user.username:
        result = await db.execute(
            select(User).where(User.username == data.username)
        )
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise ConflictError("Username already taken")

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)

    await db.commit()
    await db.refresh(current_user)

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=UserProfileResponse.model_validate(current_user),
    )


@router.post("/change-password")
async def change_user_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[MessageResponse]:
    """Change current user's password."""
    ctx = get_context()

    await change_password(
        db=db,
        user=current_user,
        current_password=data.current_password,
        new_password=data.new_password,
    )

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=MessageResponse(message="Password changed successfully"),
    )


@router.post("/delete-account")
async def delete_user_account(
    data: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[MessageResponse]:
    """Delete current user's account (soft delete)."""
    ctx = get_context()

    await delete_account(
        db=db,
        user=current_user,
        password=data.password,
    )

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=MessageResponse(message="Account deleted successfully"),
    )


@router.get("/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[UserStatsResponse]:
    """Get current user's usage statistics."""
    ctx = get_context()

    # Count conversations
    conv_result = await db.execute(
        select(func.count(Conversation.id)).where(
            Conversation.user_id == current_user.id
        )
    )
    conversations_count = conv_result.scalar() or 0

    # Count documents
    doc_result = await db.execute(
        select(func.count(Document.id)).where(Document.user_id == current_user.id)
    )
    documents_count = doc_result.scalar() or 0

    # Count agents (user-created only)
    agent_result = await db.execute(
        select(func.count(Agent.id)).where(Agent.user_id == current_user.id)
    )
    agents_count = agent_result.scalar() or 0

    # Count total messages (via conversations)
    msg_result = await db.execute(
        select(func.count(Message.id))
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(Conversation.user_id == current_user.id)
    )
    total_messages = msg_result.scalar() or 0

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=UserStatsResponse(
            conversations_count=conversations_count,
            documents_count=documents_count,
            agents_count=agents_count,
            total_messages=total_messages,
        ),
    )
