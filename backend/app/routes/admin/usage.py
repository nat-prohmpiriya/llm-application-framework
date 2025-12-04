"""Admin Usage Analytics API endpoints."""

from fastapi import APIRouter, Depends

from app.core.context import get_context
from app.core.dependencies import require_admin
from app.models.user import User
from app.schemas.admin import UsageAnalyticsResponse
from app.schemas.base import BaseResponse
from app.services import admin_usage as usage_service

router = APIRouter(prefix="/usage", tags=["admin-usage"])


@router.get("")
async def get_usage_analytics(
    days: int = 30,
    _admin: User = Depends(require_admin),
) -> BaseResponse[UsageAnalyticsResponse]:
    """Get usage analytics for admin dashboard (admin only)."""
    ctx = get_context()

    # Clamp days to reasonable range
    days = max(1, min(days, 365))

    analytics = await usage_service.get_usage_analytics(days=days)

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=UsageAnalyticsResponse(**analytics),
    )
