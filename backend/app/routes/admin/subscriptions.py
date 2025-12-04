"""Admin Subscription API endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import get_context
from app.core.dependencies import get_db, require_admin
from app.models.subscription import SubscriptionStatus
from app.models.user import User
from app.schemas.base import BaseResponse
from app.schemas.subscription import (
    PlanSummary,
    SubscriptionCancel,
    SubscriptionCreate,
    SubscriptionDetailResponse,
    SubscriptionDowngrade,
    SubscriptionFilter,
    SubscriptionListResponse,
    SubscriptionResponse,
    SubscriptionUpgrade,
    UserSummary,
)
from app.services import subscription as subscription_service

router = APIRouter(prefix="/subscriptions", tags=["admin-subscriptions"])


def _build_subscription_detail(subscription) -> SubscriptionDetailResponse:
    """Build subscription detail response with user and plan info."""
    return SubscriptionDetailResponse(
        **SubscriptionResponse.model_validate(subscription).model_dump(),
        user=UserSummary(
            id=subscription.user.id,
            email=subscription.user.email,
            username=subscription.user.username,
        ),
        plan=PlanSummary(
            id=subscription.plan.id,
            name=subscription.plan.name,
            display_name=subscription.plan.display_name,
            price_monthly=float(subscription.plan.price_monthly),
            price_yearly=float(subscription.plan.price_yearly) if subscription.plan.price_yearly else None,
        ),
    )


@router.get("")
async def list_subscriptions(
    page: int = 1,
    per_page: int = 20,
    status: SubscriptionStatus | None = None,
    plan_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> BaseResponse[SubscriptionListResponse]:
    """List all subscriptions with optional filters (admin only)."""
    ctx = get_context()

    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 20

    filters = SubscriptionFilter(
        status=status,
        plan_id=plan_id,
        user_id=user_id,
    )

    subscriptions, total = await subscription_service.get_subscriptions(
        db=db,
        page=page,
        per_page=per_page,
        filters=filters,
    )

    pages = subscription_service.calculate_pages(total, per_page)

    items = [_build_subscription_detail(sub) for sub in subscriptions]

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=SubscriptionListResponse(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            pages=pages,
        ),
    )


@router.post("", status_code=201)
async def create_subscription(
    data: SubscriptionCreate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> BaseResponse[SubscriptionDetailResponse]:
    """Create a new subscription for a user (admin only)."""
    ctx = get_context()

    try:
        subscription = await subscription_service.create_subscription(db=db, data=data)
        await db.commit()

        # Reload with relationships
        subscription = await subscription_service.get_subscription(db, subscription.id)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=_build_subscription_detail(subscription),
    )


@router.get("/{subscription_id}")
async def get_subscription(
    subscription_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> BaseResponse[SubscriptionDetailResponse]:
    """Get a subscription by ID (admin only)."""
    ctx = get_context()

    subscription = await subscription_service.get_subscription(db, subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=_build_subscription_detail(subscription),
    )


@router.post("/{subscription_id}/upgrade")
async def upgrade_subscription(
    subscription_id: uuid.UUID,
    data: SubscriptionUpgrade,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> BaseResponse[SubscriptionDetailResponse]:
    """Upgrade a subscription to a higher tier plan (admin only)."""
    ctx = get_context()

    try:
        subscription = await subscription_service.upgrade_subscription(
            db=db,
            subscription_id=subscription_id,
            data=data,
        )
        await db.commit()

        # Reload with relationships
        subscription = await subscription_service.get_subscription(db, subscription.id)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=_build_subscription_detail(subscription),
    )


@router.post("/{subscription_id}/downgrade")
async def downgrade_subscription(
    subscription_id: uuid.UUID,
    data: SubscriptionDowngrade,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> BaseResponse[SubscriptionDetailResponse]:
    """Downgrade a subscription to a lower tier plan (admin only)."""
    ctx = get_context()

    try:
        subscription = await subscription_service.downgrade_subscription(
            db=db,
            subscription_id=subscription_id,
            data=data,
        )
        await db.commit()

        # Reload with relationships
        subscription = await subscription_service.get_subscription(db, subscription.id)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=_build_subscription_detail(subscription),
    )


@router.post("/{subscription_id}/cancel")
async def cancel_subscription(
    subscription_id: uuid.UUID,
    data: SubscriptionCancel,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> BaseResponse[SubscriptionDetailResponse]:
    """Cancel a subscription (admin only)."""
    ctx = get_context()

    try:
        subscription = await subscription_service.cancel_subscription(
            db=db,
            subscription_id=subscription_id,
            data=data,
        )
        await db.commit()

        # Reload with relationships
        subscription = await subscription_service.get_subscription(db, subscription.id)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=_build_subscription_detail(subscription),
    )


@router.post("/{subscription_id}/reactivate")
async def reactivate_subscription(
    subscription_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> BaseResponse[SubscriptionDetailResponse]:
    """Reactivate a canceled subscription (admin only)."""
    ctx = get_context()

    try:
        subscription = await subscription_service.reactivate_subscription(
            db=db,
            subscription_id=subscription_id,
        )
        await db.commit()

        # Reload with relationships
        subscription = await subscription_service.get_subscription(db, subscription.id)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=_build_subscription_detail(subscription),
    )
