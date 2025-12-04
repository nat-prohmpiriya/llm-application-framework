"""Admin Dashboard API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import get_context
from app.core.dependencies import get_db, require_admin
from app.models.user import User
from app.schemas.admin import DashboardStats
from app.schemas.base import BaseResponse
from app.services import admin_stats

router = APIRouter(prefix="/dashboard", tags=["admin-dashboard"])


@router.get("")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> BaseResponse[DashboardStats]:
    """Get dashboard statistics (admin only)."""
    ctx = get_context()

    stats = await admin_stats.get_dashboard_stats(db)

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=stats,
    )
