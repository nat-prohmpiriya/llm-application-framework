"""Subscription service for managing user subscriptions."""

import logging
import uuid
from datetime import UTC, datetime, timedelta
from math import ceil

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.telemetry import traced
from app.models.subscription import BillingInterval, Subscription, SubscriptionStatus
from app.models.user import User
from app.schemas.subscription import (
    SubscriptionCancel,
    SubscriptionCreate,
    SubscriptionDowngrade,
    SubscriptionFilter,
    SubscriptionUpgrade,
)
from app.services import litellm_keys
from app.services.plan import get_plan

logger = logging.getLogger(__name__)


@traced()
async def create_subscription(
    db: AsyncSession,
    data: SubscriptionCreate,
) -> Subscription:
    """
    Create a new subscription for a user.

    Args:
        db: Database session
        data: Subscription creation data

    Returns:
        Created Subscription instance
    """
    # Get plan
    plan = await get_plan(db, data.plan_id)
    if not plan:
        raise ValueError("Plan not found")

    if not plan.is_active:
        raise ValueError("Plan is not active")

    # Get user
    stmt = select(User).where(User.id == data.user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")

    # Check for existing active subscription
    existing = await get_active_subscription(db, data.user_id)
    if existing:
        raise ValueError("User already has an active subscription")

    now = datetime.now(UTC)
    trial_end = None

    if data.trial_days:
        trial_end = now + timedelta(days=data.trial_days)

    # Calculate period end based on billing interval
    if data.billing_interval == BillingInterval.YEARLY:
        period_end = now + timedelta(days=365)
    else:
        period_end = now + timedelta(days=30)

    subscription = Subscription(
        user_id=data.user_id,
        plan_id=data.plan_id,
        status=SubscriptionStatus.TRIALING if trial_end else SubscriptionStatus.ACTIVE,
        billing_interval=data.billing_interval,
        start_date=now,
        trial_end_date=trial_end,
        current_period_start=now,
        current_period_end=period_end,
    )
    db.add(subscription)
    await db.flush()

    # Create LiteLLM virtual key
    try:
        key_result = await litellm_keys.create_virtual_key(
            user_id=data.user_id,
            plan=plan,
            user_email=user.email,
        )
        subscription.litellm_key_id = key_result.get("key_id")
    except litellm_keys.LiteLLMKeyError as e:
        logger.warning(f"Failed to create LiteLLM key: {e}")

    # Update user tier
    user.tier = plan.plan_type.value
    await db.flush()

    logger.info(f"Created subscription {subscription.id} for user {data.user_id}")
    return subscription


@traced()
async def get_subscription(
    db: AsyncSession,
    subscription_id: uuid.UUID,
) -> Subscription | None:
    """
    Get a subscription by ID.

    Args:
        db: Database session
        subscription_id: Subscription ID

    Returns:
        Subscription if found, None otherwise
    """
    stmt = (
        select(Subscription)
        .options(selectinload(Subscription.user), selectinload(Subscription.plan))
        .where(Subscription.id == subscription_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


@traced()
async def get_active_subscription(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> Subscription | None:
    """
    Get the active subscription for a user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Active subscription if found, None otherwise
    """
    stmt = (
        select(Subscription)
        .options(selectinload(Subscription.plan))
        .where(
            Subscription.user_id == user_id,
            Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]),
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


@traced()
async def get_subscriptions(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
    filters: SubscriptionFilter | None = None,
) -> tuple[list[Subscription], int]:
    """
    Get paginated subscriptions with optional filters.

    Args:
        db: Database session
        page: Page number (1-indexed)
        per_page: Items per page
        filters: Optional filter criteria

    Returns:
        Tuple of (subscriptions list, total count)
    """
    base_query = select(Subscription).options(
        selectinload(Subscription.user),
        selectinload(Subscription.plan),
    )
    count_query = select(func.count(Subscription.id))

    if filters:
        if filters.status:
            base_query = base_query.where(Subscription.status == filters.status)
            count_query = count_query.where(Subscription.status == filters.status)
        if filters.plan_id:
            base_query = base_query.where(Subscription.plan_id == filters.plan_id)
            count_query = count_query.where(Subscription.plan_id == filters.plan_id)
        if filters.user_id:
            base_query = base_query.where(Subscription.user_id == filters.user_id)
            count_query = count_query.where(Subscription.user_id == filters.user_id)

    # Count total
    total = (await db.execute(count_query)).scalar() or 0

    # Get paginated subscriptions
    offset = (page - 1) * per_page
    stmt = base_query.order_by(Subscription.created_at.desc()).offset(offset).limit(per_page)
    result = await db.execute(stmt)
    subscriptions = list(result.scalars().all())

    return subscriptions, total


@traced()
async def upgrade_subscription(
    db: AsyncSession,
    subscription_id: uuid.UUID,
    data: SubscriptionUpgrade,
) -> Subscription:
    """
    Upgrade a subscription to a higher tier plan.

    Args:
        db: Database session
        subscription_id: Subscription ID
        data: Upgrade data

    Returns:
        Updated Subscription
    """
    subscription = await get_subscription(db, subscription_id)
    if not subscription:
        raise ValueError("Subscription not found")

    if subscription.status not in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]:
        raise ValueError("Cannot upgrade inactive subscription")

    # Get new plan
    new_plan = await get_plan(db, data.new_plan_id)
    if not new_plan:
        raise ValueError("New plan not found")

    if not new_plan.is_active:
        raise ValueError("New plan is not active")

    # Verify it's an upgrade (higher price)
    old_plan = subscription.plan
    if new_plan.price_monthly <= old_plan.price_monthly:
        raise ValueError("New plan must have higher price for upgrade. Use downgrade instead.")

    # Update subscription
    subscription.plan_id = data.new_plan_id
    if data.billing_interval:
        subscription.billing_interval = data.billing_interval

    # Update LiteLLM key with new plan limits
    if subscription.litellm_key_id:
        try:
            await litellm_keys.update_virtual_key(subscription.litellm_key_id, new_plan)
        except litellm_keys.LiteLLMKeyError as e:
            logger.warning(f"Failed to update LiteLLM key: {e}")

    # Update user tier
    user_stmt = select(User).where(User.id == subscription.user_id)
    result = await db.execute(user_stmt)
    user = result.scalar_one_or_none()
    if user:
        user.tier = new_plan.plan_type.value

    await db.flush()
    logger.info(f"Upgraded subscription {subscription_id} to plan {new_plan.name}")

    return subscription


@traced()
async def downgrade_subscription(
    db: AsyncSession,
    subscription_id: uuid.UUID,
    data: SubscriptionDowngrade,
) -> Subscription:
    """
    Downgrade a subscription to a lower tier plan.

    Args:
        db: Database session
        subscription_id: Subscription ID
        data: Downgrade data

    Returns:
        Updated Subscription
    """
    subscription = await get_subscription(db, subscription_id)
    if not subscription:
        raise ValueError("Subscription not found")

    if subscription.status not in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]:
        raise ValueError("Cannot downgrade inactive subscription")

    # Get new plan
    new_plan = await get_plan(db, data.new_plan_id)
    if not new_plan:
        raise ValueError("New plan not found")

    if not new_plan.is_active:
        raise ValueError("New plan is not active")

    # Verify it's a downgrade (lower or equal price)
    old_plan = subscription.plan
    if new_plan.price_monthly > old_plan.price_monthly:
        raise ValueError("New plan must have lower price for downgrade. Use upgrade instead.")

    if data.effective_at_period_end:
        # Schedule downgrade at end of current period
        # For now, just update immediately (TODO: implement scheduled changes)
        pass

    # Update subscription
    subscription.plan_id = data.new_plan_id
    if data.billing_interval:
        subscription.billing_interval = data.billing_interval

    # Update LiteLLM key with new plan limits
    if subscription.litellm_key_id:
        try:
            await litellm_keys.update_virtual_key(subscription.litellm_key_id, new_plan)
        except litellm_keys.LiteLLMKeyError as e:
            logger.warning(f"Failed to update LiteLLM key: {e}")

    # Update user tier
    user_stmt = select(User).where(User.id == subscription.user_id)
    result = await db.execute(user_stmt)
    user = result.scalar_one_or_none()
    if user:
        user.tier = new_plan.plan_type.value

    await db.flush()
    logger.info(f"Downgraded subscription {subscription_id} to plan {new_plan.name}")

    return subscription


@traced()
async def cancel_subscription(
    db: AsyncSession,
    subscription_id: uuid.UUID,
    data: SubscriptionCancel,
) -> Subscription:
    """
    Cancel a subscription.

    Args:
        db: Database session
        subscription_id: Subscription ID
        data: Cancellation data

    Returns:
        Updated Subscription
    """
    subscription = await get_subscription(db, subscription_id)
    if not subscription:
        raise ValueError("Subscription not found")

    if subscription.status == SubscriptionStatus.CANCELED:
        raise ValueError("Subscription is already canceled")

    now = datetime.now(UTC)

    if data.cancel_at_period_end and subscription.current_period_end:
        # Set to cancel at end of current period
        subscription.end_date = subscription.current_period_end
    else:
        # Cancel immediately
        subscription.status = SubscriptionStatus.CANCELED
        subscription.end_date = now

    subscription.canceled_at = now
    subscription.cancel_reason = data.cancel_reason

    # Disable LiteLLM key if canceling immediately
    if not data.cancel_at_period_end and subscription.litellm_key_id:
        try:
            await litellm_keys.disable_virtual_key(subscription.litellm_key_id)
        except litellm_keys.LiteLLMKeyError as e:
            logger.warning(f"Failed to disable LiteLLM key: {e}")

    # Update user tier to free if canceling immediately
    if not data.cancel_at_period_end:
        user_stmt = select(User).where(User.id == subscription.user_id)
        result = await db.execute(user_stmt)
        user = result.scalar_one_or_none()
        if user:
            user.tier = "free"

    await db.flush()
    logger.info(f"Canceled subscription {subscription_id}")

    return subscription


@traced()
async def reactivate_subscription(
    db: AsyncSession,
    subscription_id: uuid.UUID,
) -> Subscription:
    """
    Reactivate a canceled subscription (if still in period).

    Args:
        db: Database session
        subscription_id: Subscription ID

    Returns:
        Updated Subscription
    """
    subscription = await get_subscription(db, subscription_id)
    if not subscription:
        raise ValueError("Subscription not found")

    now = datetime.now(UTC)

    # Can only reactivate if not yet expired
    if subscription.end_date and subscription.end_date < now:
        raise ValueError("Subscription has expired, please create a new subscription")

    if subscription.status not in [SubscriptionStatus.CANCELED, SubscriptionStatus.PAUSED]:
        raise ValueError("Subscription is not canceled or paused")

    subscription.status = SubscriptionStatus.ACTIVE
    subscription.canceled_at = None
    subscription.end_date = None
    subscription.cancel_reason = None

    # Re-enable LiteLLM key
    if subscription.litellm_key_id:
        try:
            await litellm_keys.update_virtual_key(subscription.litellm_key_id, subscription.plan)
        except litellm_keys.LiteLLMKeyError as e:
            logger.warning(f"Failed to update LiteLLM key: {e}")

    # Update user tier
    user_stmt = select(User).where(User.id == subscription.user_id)
    result = await db.execute(user_stmt)
    user = result.scalar_one_or_none()
    if user:
        user.tier = subscription.plan.plan_type.value

    await db.flush()
    logger.info(f"Reactivated subscription {subscription_id}")

    return subscription


@traced()
async def update_subscription_from_stripe(
    db: AsyncSession,
    stripe_subscription_id: str,
    status: SubscriptionStatus,
    current_period_start: datetime | None = None,
    current_period_end: datetime | None = None,
) -> Subscription | None:
    """
    Update subscription status from Stripe webhook.

    Args:
        db: Database session
        stripe_subscription_id: Stripe subscription ID
        status: New status
        current_period_start: Period start from Stripe
        current_period_end: Period end from Stripe

    Returns:
        Updated Subscription or None if not found
    """
    stmt = select(Subscription).where(
        Subscription.stripe_subscription_id == stripe_subscription_id
    )
    result = await db.execute(stmt)
    subscription = result.scalar_one_or_none()

    if not subscription:
        logger.warning(f"Subscription not found for Stripe ID: {stripe_subscription_id}")
        return None

    subscription.status = status

    if current_period_start:
        subscription.current_period_start = current_period_start
    if current_period_end:
        subscription.current_period_end = current_period_end

    # Handle status changes
    if status == SubscriptionStatus.CANCELED:
        subscription.canceled_at = datetime.now(UTC)
        if subscription.litellm_key_id:
            try:
                await litellm_keys.disable_virtual_key(subscription.litellm_key_id)
            except litellm_keys.LiteLLMKeyError:
                pass

    await db.flush()
    logger.info(f"Updated subscription {subscription.id} from Stripe webhook")

    return subscription


def calculate_pages(total: int, per_page: int) -> int:
    """Calculate total number of pages."""
    return ceil(total / per_page) if per_page > 0 else 0
