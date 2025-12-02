"""Conversation service for managing chat history."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole


async def list_conversations(
    db: AsyncSession,
    user_id: uuid.UUID,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[Conversation], int]:
    """
    List user's conversations with pagination.

    Returns:
        Tuple of (conversations list, total count)
    """
    # Get total count
    count_stmt = (
        select(func.count())
        .select_from(Conversation)
        .where(Conversation.user_id == user_id)
    )
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # Get paginated conversations
    offset = (page - 1) * per_page
    stmt = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    result = await db.execute(stmt)
    conversations = list(result.scalars().all())

    return conversations, total


async def get_conversation_message_count(
    db: AsyncSession,
    conversation_id: uuid.UUID,
) -> int:
    """Get message count for a conversation."""
    stmt = (
        select(func.count())
        .select_from(Message)
        .where(Message.conversation_id == conversation_id)
    )
    result = await db.execute(stmt)
    return result.scalar() or 0


async def get_last_message_preview(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    max_length: int = 100,
) -> str | None:
    """Get preview of the last message in a conversation."""
    stmt = (
        select(Message.content)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    content = result.scalar_one_or_none()

    if content:
        return content[:max_length] + "..." if len(content) > max_length else content
    return None


async def create_conversation(
    db: AsyncSession,
    user_id: uuid.UUID,
    title: str | None = None,
    project_id: uuid.UUID | None = None,
) -> Conversation:
    """Create a new conversation."""
    conversation = Conversation(
        user_id=user_id,
        title=title,
        project_id=project_id,
    )
    db.add(conversation)
    await db.flush()
    await db.refresh(conversation)
    return conversation


async def get_conversation(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Conversation:
    """
    Get conversation with messages by ID.

    Raises:
        NotFoundError: If conversation not found
        ForbiddenError: If user doesn't own the conversation
    """
    stmt = (
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.id == conversation_id)
    )
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise NotFoundError("Conversation not found")

    if conversation.user_id != user_id:
        raise ForbiddenError("You don't have access to this conversation")

    return conversation


async def get_conversation_simple(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Conversation:
    """
    Get conversation by ID without loading messages.

    Raises:
        NotFoundError: If conversation not found
        ForbiddenError: If user doesn't own the conversation
    """
    stmt = select(Conversation).where(Conversation.id == conversation_id)
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise NotFoundError("Conversation not found")

    if conversation.user_id != user_id:
        raise ForbiddenError("You don't have access to this conversation")

    return conversation


async def update_conversation(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    user_id: uuid.UUID,
    title: str | None = None,
) -> Conversation:
    """
    Update conversation title.

    Raises:
        NotFoundError: If conversation not found
        ForbiddenError: If user doesn't own the conversation
    """
    conversation = await get_conversation_simple(db, conversation_id, user_id)

    if title is not None:
        conversation.title = title

    await db.flush()
    await db.refresh(conversation)
    return conversation


async def delete_conversation(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    user_id: uuid.UUID,
) -> bool:
    """
    Delete a conversation.

    Raises:
        NotFoundError: If conversation not found
        ForbiddenError: If user doesn't own the conversation
    """
    conversation = await get_conversation_simple(db, conversation_id, user_id)
    await db.delete(conversation)
    await db.flush()
    return True


async def add_message(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    role: str,
    content: str,
    tokens_used: int | None = None,
) -> Message:
    """Add a message to a conversation."""
    # Convert string role to MessageRole enum
    message_role = MessageRole(role)

    message = Message(
        conversation_id=conversation_id,
        role=message_role,
        content=content,
        tokens_used=tokens_used,
    )
    db.add(message)
    await db.flush()
    await db.refresh(message)
    return message


async def get_conversation_messages(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    user_id: uuid.UUID,
    limit: int | None = None,
) -> list[Message]:
    """
    Get messages for a conversation.

    Raises:
        NotFoundError: If conversation not found
        ForbiddenError: If user doesn't own the conversation
    """
    # Verify ownership first
    await get_conversation_simple(db, conversation_id, user_id)

    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )

    if limit:
        stmt = stmt.limit(limit)

    result = await db.execute(stmt)
    return list(result.scalars().all())
