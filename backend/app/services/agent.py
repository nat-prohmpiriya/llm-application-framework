"""Agent service for managing user-created agents."""

import logging
import uuid
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.telemetry import traced
from app.models.agent import Agent, AgentSource
from app.schemas.agent import AgentCreate, AgentUpdate
from app.services.agent_loader import agent_loader

logger = logging.getLogger(__name__)


@traced()
async def create_agent(
    db: AsyncSession,
    user_id: uuid.UUID,
    data: AgentCreate,
) -> Agent:
    """
    Create a new user agent.

    Args:
        db: Database session
        user_id: User ID
        data: Agent creation data

    Returns:
        Created Agent instance
    """
    # Convert tools to list of strings
    tools = [t.value if hasattr(t, "value") else str(t) for t in (data.tools or [])]

    agent = Agent(
        user_id=user_id,
        project_id=data.project_id,
        name=data.name,
        slug=data.slug,
        description=data.description,
        icon=data.icon,
        system_prompt=data.system_prompt,
        tools=tools,
        config=data.config,
        is_active=data.is_active,
        source=AgentSource.user.value,
        document_ids=data.document_ids,
    )
    db.add(agent)
    await db.flush()
    await db.refresh(agent)

    logger.info(f"Created agent {agent.id} ({agent.slug}) for user {user_id}")
    return agent


@traced()
async def get_agent_by_id(
    db: AsyncSession,
    agent_id: uuid.UUID,
    user_id: uuid.UUID | None = None,
) -> Agent | None:
    """
    Get an agent by ID.

    Args:
        db: Database session
        agent_id: Agent ID
        user_id: Optional user ID for ownership check

    Returns:
        Agent if found, None otherwise
    """
    stmt = select(Agent).where(Agent.id == agent_id)
    if user_id:
        stmt = stmt.where(Agent.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


@traced()
async def get_agent_by_slug(
    db: AsyncSession,
    slug: str,
    user_id: uuid.UUID | None = None,
) -> Agent | None:
    """
    Get an agent by slug.

    Args:
        db: Database session
        slug: Agent slug
        user_id: Optional user ID for ownership check

    Returns:
        Agent if found, None otherwise
    """
    stmt = select(Agent).where(Agent.slug == slug)
    if user_id:
        # For user agents, check ownership
        stmt = stmt.where(
            or_(
                Agent.source == AgentSource.system.value,
                Agent.user_id == user_id,
            )
        )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


@traced()
async def get_user_agents(
    db: AsyncSession,
    user_id: uuid.UUID,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[Agent], int]:
    """
    Get paginated agents for a user.

    Args:
        db: Database session
        user_id: User ID
        page: Page number (1-indexed)
        per_page: Items per page

    Returns:
        Tuple of (agents list, total count)
    """
    # Count total user agents
    count_stmt = select(func.count(Agent.id)).where(
        Agent.user_id == user_id,
        Agent.source == AgentSource.user.value,
    )
    total = (await db.execute(count_stmt)).scalar() or 0

    # Get paginated agents
    offset = (page - 1) * per_page
    stmt = (
        select(Agent)
        .where(Agent.user_id == user_id, Agent.source == AgentSource.user.value)
        .order_by(Agent.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    result = await db.execute(stmt)
    agents = list(result.scalars().all())

    return agents, total


@traced()
async def get_all_agents_for_user(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> list[dict[str, Any]]:
    """
    Get all agents available to a user (system + user's own).

    Args:
        db: Database session
        user_id: User ID

    Returns:
        List of agent dicts with source field
    """
    agents: list[dict[str, Any]] = []

    # 1. Get system agents from YAML
    system_agents = agent_loader.list_agents()
    for agent in system_agents:
        agents.append({
            "id": None,  # System agents don't have DB id
            "user_id": None,
            "project_id": None,
            "name": agent.get("name", ""),
            "slug": agent.get("slug", ""),
            "description": agent.get("description"),
            "icon": agent.get("icon"),
            "system_prompt": None,  # Don't expose system prompt in list
            "tools": agent.get("tools", []),
            "config": agent.get("settings"),
            "is_active": True,
            "source": AgentSource.system.value,
            "document_ids": None,
            "created_at": None,
            "updated_at": None,
        })

    # 2. Get user's own agents from DB
    stmt = (
        select(Agent)
        .where(Agent.user_id == user_id, Agent.source == AgentSource.user.value)
        .order_by(Agent.created_at.desc())
    )
    result = await db.execute(stmt)
    user_agents = result.scalars().all()

    for agent in user_agents:
        agents.append({
            "id": agent.id,
            "user_id": agent.user_id,
            "project_id": agent.project_id,
            "name": agent.name,
            "slug": agent.slug,
            "description": agent.description,
            "icon": agent.icon,
            "system_prompt": agent.system_prompt,
            "tools": agent.tools or [],
            "config": agent.config,
            "is_active": agent.is_active,
            "source": agent.source,
            "document_ids": agent.document_ids,
            "created_at": agent.created_at,
            "updated_at": agent.updated_at,
        })

    return agents


@traced()
async def update_agent(
    db: AsyncSession,
    agent_id: uuid.UUID,
    user_id: uuid.UUID,
    data: AgentUpdate,
) -> Agent | None:
    """
    Update a user agent (owner only).

    Args:
        db: Database session
        agent_id: Agent ID
        user_id: User ID for ownership check
        data: Agent update data

    Returns:
        Updated Agent if found and owned by user, None otherwise
    """
    agent = await get_agent_by_id(db, agent_id, user_id)
    if not agent:
        return None

    # Can only update user agents
    if agent.source != AgentSource.user.value:
        logger.warning(f"Attempt to update system agent {agent_id}")
        return None

    if data.name is not None:
        agent.name = data.name
    if data.slug is not None:
        agent.slug = data.slug
    if data.description is not None:
        agent.description = data.description
    if data.icon is not None:
        agent.icon = data.icon
    if data.system_prompt is not None:
        agent.system_prompt = data.system_prompt
    if data.tools is not None:
        agent.tools = [t.value if hasattr(t, "value") else str(t) for t in data.tools]
    if data.config is not None:
        agent.config = data.config
    if data.is_active is not None:
        agent.is_active = data.is_active
    if data.project_id is not None:
        agent.project_id = data.project_id
    if data.document_ids is not None:
        agent.document_ids = data.document_ids

    await db.flush()
    await db.refresh(agent)
    logger.info(f"Updated agent {agent_id}")
    return agent


@traced()
async def delete_agent(
    db: AsyncSession,
    agent_id: uuid.UUID,
    user_id: uuid.UUID,
) -> bool:
    """
    Delete a user agent (owner only).

    Args:
        db: Database session
        agent_id: Agent ID
        user_id: User ID for ownership check

    Returns:
        True if deleted, False if not found or not owned
    """
    agent = await get_agent_by_id(db, agent_id, user_id)
    if not agent:
        return False

    # Can only delete user agents
    if agent.source != AgentSource.user.value:
        logger.warning(f"Attempt to delete system agent {agent_id}")
        return False

    await db.delete(agent)
    await db.flush()

    logger.info(f"Deleted agent {agent_id}")
    return True


@traced()
async def check_slug_exists(
    db: AsyncSession,
    slug: str,
    exclude_id: uuid.UUID | None = None,
) -> bool:
    """
    Check if an agent slug already exists.

    Args:
        db: Database session
        slug: Slug to check
        exclude_id: Optional agent ID to exclude (for updates)

    Returns:
        True if slug exists, False otherwise
    """
    # Check system agents
    system_agents = agent_loader.list_agents()
    for agent in system_agents:
        if agent.get("slug") == slug:
            return True

    # Check DB agents
    stmt = select(Agent.id).where(Agent.slug == slug)
    if exclude_id:
        stmt = stmt.where(Agent.id != exclude_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None
