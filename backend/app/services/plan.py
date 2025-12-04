"""Plan service for managing subscription plans."""

import logging
import uuid
from math import ceil

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.telemetry import traced
from app.models.plan import Plan
from app.models.subscription import Subscription, SubscriptionStatus
from app.schemas.plan import PlanCreate, PlanUpdate

logger = logging.getLogger(__name__)


@traced()
async def create_plan(
    db: AsyncSession,
    data: PlanCreate,
) -> Plan:
    """
    Create a new plan.

    Args:
        db: Database session
        data: Plan creation data

    Returns:
        Created Plan instance
    """
    plan = Plan(
        name=data.name,
        display_name=data.display_name,
        description=data.description,
        plan_type=data.plan_type,
        price_monthly=data.price_monthly,
        price_yearly=data.price_yearly,
        currency=data.currency,
        tokens_per_month=data.tokens_per_month,
        requests_per_minute=data.requests_per_minute,
        requests_per_day=data.requests_per_day,
        max_documents=data.max_documents,
        max_projects=data.max_projects,
        max_agents=data.max_agents,
        allowed_models=data.allowed_models,
        features=data.features,
        is_active=data.is_active,
        is_public=data.is_public,
        stripe_price_id_monthly=data.stripe_price_id_monthly,
        stripe_price_id_yearly=data.stripe_price_id_yearly,
        stripe_product_id=data.stripe_product_id,
    )
    db.add(plan)
    await db.flush()

    logger.info(f"Created plan {plan.id}: {plan.name}")
    return plan


@traced()
async def get_plan(
    db: AsyncSession,
    plan_id: uuid.UUID,
) -> Plan | None:
    """
    Get a plan by ID.

    Args:
        db: Database session
        plan_id: Plan ID

    Returns:
        Plan if found, None otherwise
    """
    stmt = select(Plan).where(Plan.id == plan_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


@traced()
async def get_plan_by_name(
    db: AsyncSession,
    name: str,
) -> Plan | None:
    """
    Get a plan by name.

    Args:
        db: Database session
        name: Plan name

    Returns:
        Plan if found, None otherwise
    """
    stmt = select(Plan).where(Plan.name == name)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


@traced()
async def get_plans(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
    include_inactive: bool = False,
) -> tuple[list[Plan], int]:
    """
    Get paginated plans.

    Args:
        db: Database session
        page: Page number (1-indexed)
        per_page: Items per page
        include_inactive: Whether to include inactive plans

    Returns:
        Tuple of (plans list, total count)
    """
    base_query = select(Plan)
    count_query = select(func.count(Plan.id))

    if not include_inactive:
        base_query = base_query.where(Plan.is_active.is_(True))
        count_query = count_query.where(Plan.is_active.is_(True))

    # Count total
    total = (await db.execute(count_query)).scalar() or 0

    # Get paginated plans
    offset = (page - 1) * per_page
    stmt = base_query.order_by(Plan.price_monthly.asc()).offset(offset).limit(per_page)
    result = await db.execute(stmt)
    plans = list(result.scalars().all())

    return plans, total


@traced()
async def get_subscriber_count(
    db: AsyncSession,
    plan_id: uuid.UUID,
) -> int:
    """
    Get the number of active subscribers for a plan.

    Args:
        db: Database session
        plan_id: Plan ID

    Returns:
        Number of active subscribers
    """
    stmt = select(func.count(Subscription.id)).where(
        Subscription.plan_id == plan_id,
        Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]),
    )
    result = await db.execute(stmt)
    return result.scalar() or 0


@traced()
async def get_plans_with_subscriber_counts(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
    include_inactive: bool = True,
) -> tuple[list[tuple[Plan, int]], int]:
    """
    Get paginated plans with subscriber counts.

    Args:
        db: Database session
        page: Page number (1-indexed)
        per_page: Items per page
        include_inactive: Whether to include inactive plans

    Returns:
        Tuple of (list of (plan, subscriber_count) tuples, total count)
    """
    plans, total = await get_plans(db, page, per_page, include_inactive)

    plans_with_counts = []
    for plan in plans:
        count = await get_subscriber_count(db, plan.id)
        plans_with_counts.append((plan, count))

    return plans_with_counts, total


@traced()
async def update_plan(
    db: AsyncSession,
    plan_id: uuid.UUID,
    data: PlanUpdate,
) -> Plan | None:
    """
    Update a plan.

    Args:
        db: Database session
        plan_id: Plan ID
        data: Plan update data

    Returns:
        Updated Plan if found, None otherwise
    """
    plan = await get_plan(db, plan_id)
    if not plan:
        return None

    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(plan, field, value)

    await db.flush()
    logger.info(f"Updated plan {plan_id}")
    return plan


@traced()
async def delete_plan(
    db: AsyncSession,
    plan_id: uuid.UUID,
) -> bool:
    """
    Delete a plan (soft delete by setting is_active=False).

    Args:
        db: Database session
        plan_id: Plan ID

    Returns:
        True if deleted, False if not found
    """
    plan = await get_plan(db, plan_id)
    if not plan:
        return False

    # Check if there are active subscribers
    subscriber_count = await get_subscriber_count(db, plan_id)
    if subscriber_count > 0:
        raise ValueError(f"Cannot delete plan with {subscriber_count} active subscribers")

    await db.delete(plan)
    await db.flush()

    logger.info(f"Deleted plan {plan_id}")
    return True


@traced()
async def get_active_subscriptions_for_plan(
    db: AsyncSession,
    plan_id: uuid.UUID,
) -> list[Subscription]:
    """
    Get all active subscriptions for a plan.

    Args:
        db: Database session
        plan_id: Plan ID

    Returns:
        List of active subscriptions
    """
    stmt = select(Subscription).where(
        Subscription.plan_id == plan_id,
        Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]),
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


def calculate_pages(total: int, per_page: int) -> int:
    """Calculate total number of pages."""
    return ceil(total / per_page) if per_page > 0 else 0
