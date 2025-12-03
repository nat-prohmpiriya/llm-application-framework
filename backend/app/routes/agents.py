"""Agent API routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import get_context
from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.agent import AgentCreate, AgentInfo, AgentSource, AgentUpdate
from app.schemas.base import BaseResponse
from app.services import agent as agent_service
from app.services.agent_loader import agent_loader

router = APIRouter(prefix="/agents", tags=["agents"])


class AgentListItem(BaseModel):
    """Agent list item response."""

    id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None
    project_id: uuid.UUID | None = None
    name: str
    slug: str
    icon: str | None = None
    description: str | None = None
    tools: list[str] = []
    is_active: bool = True
    source: str  # "system" or "user"
    document_ids: list[uuid.UUID] | None = None


class AgentDetailResponse(BaseModel):
    """Detailed agent response."""

    id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None
    project_id: uuid.UUID | None = None
    name: str
    slug: str
    icon: str | None = None
    description: str | None = None
    system_prompt: str | None = None
    tools: list[str] = []
    config: dict | None = None
    is_active: bool = True
    source: str
    document_ids: list[uuid.UUID] | None = None


class ToolInfo(BaseModel):
    """Tool information response."""

    name: str
    description: str


class AgentToolsResponse(BaseModel):
    """Agent tools response."""

    agent_slug: str
    tools: list[ToolInfo]


class AgentListResponse(BaseModel):
    """Agent list response."""

    agents: list[AgentListItem]
    total: int


@router.get("")
async def list_agents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[AgentListResponse]:
    """List all available agents (system + user's own)."""
    ctx = get_context()

    all_agents = await agent_service.get_all_agents_for_user(db, current_user.id)

    agents = [
        AgentListItem(
            id=agent.get("id"),
            user_id=agent.get("user_id"),
            project_id=agent.get("project_id"),
            name=agent.get("name", ""),
            slug=agent.get("slug", ""),
            icon=agent.get("icon"),
            description=agent.get("description"),
            tools=agent.get("tools", []),
            is_active=agent.get("is_active", True),
            source=agent.get("source", AgentSource.system.value),
            document_ids=agent.get("document_ids"),
        )
        for agent in all_agents
    ]

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=AgentListResponse(agents=agents, total=len(agents)),
    )


@router.post("")
async def create_agent(
    data: AgentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[AgentInfo]:
    """Create a new user agent."""
    ctx = get_context()

    # Check if slug already exists
    slug_exists = await agent_service.check_slug_exists(db, data.slug)
    if slug_exists:
        raise HTTPException(status_code=400, detail=f"Agent slug already exists: {data.slug}")

    agent = await agent_service.create_agent(db, current_user.id, data)

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=AgentInfo.model_validate(agent),
    )


@router.get("/{slug}")
async def get_agent(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[AgentDetailResponse]:
    """Get agent details by slug."""
    ctx = get_context()

    # First try to find in user's DB agents
    db_agent = await agent_service.get_agent_by_slug(db, slug, current_user.id)
    if db_agent:
        return BaseResponse(
            trace_id=ctx.trace_id,
            data=AgentDetailResponse(
                id=db_agent.id,
                user_id=db_agent.user_id,
                project_id=db_agent.project_id,
                name=db_agent.name,
                slug=db_agent.slug,
                icon=db_agent.icon,
                description=db_agent.description,
                system_prompt=db_agent.system_prompt,
                tools=db_agent.tools or [],
                config=db_agent.config,
                is_active=db_agent.is_active,
                source=db_agent.source,
                document_ids=db_agent.document_ids,
            ),
        )

    # Then try system agents from YAML
    config = agent_loader.load_agent(slug)
    if not config:
        raise HTTPException(status_code=404, detail=f"Agent not found: {slug}")

    agent_info = config.get("agent", {})
    persona = config.get("persona", {})

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=AgentDetailResponse(
            id=None,
            user_id=None,
            project_id=None,
            name=agent_info.get("name", ""),
            slug=agent_info.get("slug", slug),
            icon=agent_info.get("icon"),
            description=agent_info.get("description"),
            system_prompt=persona.get("system_prompt"),
            tools=config.get("tools", []),
            config=config.get("settings"),
            is_active=True,
            source=AgentSource.system.value,
            document_ids=None,
        ),
    )


@router.put("/{agent_id}")
async def update_agent(
    agent_id: uuid.UUID,
    data: AgentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[AgentInfo]:
    """Update a user agent (owner only)."""
    ctx = get_context()

    # Check if new slug already exists (if slug is being updated)
    if data.slug:
        slug_exists = await agent_service.check_slug_exists(db, data.slug, exclude_id=agent_id)
        if slug_exists:
            raise HTTPException(status_code=400, detail=f"Agent slug already exists: {data.slug}")

    agent = await agent_service.update_agent(db, agent_id, current_user.id, data)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found or you don't have permission to update it")

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=AgentInfo.model_validate(agent),
    )


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[dict]:
    """Delete a user agent (owner only)."""
    ctx = get_context()

    deleted = await agent_service.delete_agent(db, agent_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Agent not found or you don't have permission to delete it")

    return BaseResponse(
        trace_id=ctx.trace_id,
        data={"message": "Agent deleted successfully"},
    )


@router.get("/{slug}/tools")
async def get_agent_tools(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[AgentToolsResponse]:
    """Get tools available for an agent."""
    ctx = get_context()

    # Import tool registry to get descriptions
    from app.agents.tools import TOOL_REGISTRY

    # Try to find agent (DB or system)
    agent_tools: list[str] = []

    # First check DB
    db_agent = await agent_service.get_agent_by_slug(db, slug, current_user.id)
    if db_agent:
        agent_tools = db_agent.tools or []
    else:
        # Check system agents
        config = agent_loader.load_agent(slug)
        if not config:
            raise HTTPException(status_code=404, detail=f"Agent not found: {slug}")
        agent_tools = config.get("tools", [])

    tools = []
    for tool_name in agent_tools:
        tool = TOOL_REGISTRY.get(tool_name)
        if tool:
            tools.append(ToolInfo(
                name=tool_name,
                description=tool.description,
            ))
        else:
            tools.append(ToolInfo(
                name=tool_name,
                description="Tool not available",
            ))

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=AgentToolsResponse(agent_slug=slug, tools=tools),
    )
