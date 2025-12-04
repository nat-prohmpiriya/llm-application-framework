"""Admin Notification API endpoints for broadcasting and managing notifications."""

import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import get_context
from app.core.dependencies import get_db, require_admin
from app.models.notification import Notification, NotificationCategory, NotificationType
from app.models.plan import Plan
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.user import User
from app.schemas.base import BaseResponse
from app.schemas.notification import (
    BroadcastNotificationCreate,
    BroadcastNotificationResponse,
    NotificationResponse,
)
from app.services import audit_log as audit_service
from app.services import notification as notification_service

router = APIRouter(prefix="/notifications", tags=["admin-notifications"])


# ============================================================================
# Response Schemas
# ============================================================================


class NotificationStatsResponse(BaseModel):
    """Notification statistics response."""

    total_notifications: int
    unread_notifications: int
    notifications_today: int
    notifications_this_week: int
    notifications_by_category: dict[str, int]
    notifications_by_type: dict[str, int]
    active_users_with_notifications: int


class SendNotificationRequest(BaseModel):
    """Request for sending notification to specific users."""

    user_ids: list[uuid.UUID]
    type: NotificationType = NotificationType.SYSTEM_ANNOUNCEMENT
    category: NotificationCategory = NotificationCategory.SYSTEM
    title: str
    message: str
    priority: str = "medium"
    action_url: str | None = None
    expires_at: datetime | None = None


class SendNotificationResponse(BaseModel):
    """Response for sending notifications."""

    success: bool
    notifications_created: int
    failed_user_ids: list[uuid.UUID]
    message: str


# ============================================================================
# Stats Endpoint
# ============================================================================


@router.get("/stats")
async def get_notification_stats(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> BaseResponse[NotificationStatsResponse]:
    """
    Get notification statistics for admin dashboard.

    Returns counts of notifications by category, type, and time period.
    """
    ctx = get_context()

    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    week_start = today_start - timedelta(days=7)

    # Total notifications
    total_result = await db.execute(select(func.count(Notification.id)))
    total = total_result.scalar() or 0

    # Unread notifications
    unread_result = await db.execute(
        select(func.count(Notification.id)).where(Notification.read_at.is_(None))
    )
    unread = unread_result.scalar() or 0

    # Notifications today
    today_result = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.created_at >= today_start
        )
    )
    today_count = today_result.scalar() or 0

    # Notifications this week
    week_result = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.created_at >= week_start
        )
    )
    week_count = week_result.scalar() or 0

    # By category
    category_result = await db.execute(
        select(Notification.category, func.count(Notification.id))
        .group_by(Notification.category)
    )
    by_category = {row[0]: row[1] for row in category_result.all()}

    # By type
    type_result = await db.execute(
        select(Notification.type, func.count(Notification.id))
        .group_by(Notification.type)
    )
    by_type = {row[0]: row[1] for row in type_result.all()}

    # Active users with notifications
    active_users_result = await db.execute(
        select(func.count(func.distinct(Notification.user_id)))
    )
    active_users = active_users_result.scalar() or 0

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=NotificationStatsResponse(
            total_notifications=total,
            unread_notifications=unread,
            notifications_today=today_count,
            notifications_this_week=week_count,
            notifications_by_category=by_category,
            notifications_by_type=by_type,
            active_users_with_notifications=active_users,
        ),
    )


# ============================================================================
# Broadcast Endpoint
# ============================================================================


@router.post("/broadcast")
async def broadcast_notification(
    data: BroadcastNotificationCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> BaseResponse[BroadcastNotificationResponse]:
    """
    Broadcast a notification to multiple users.

    Target options:
    - All users: Leave target_plan_id and target_user_ids empty
    - Specific plan: Set target_plan_id to filter by subscription plan
    - Specific users: Set target_user_ids to send to specific users

    Rate limiting: Maximum 1 broadcast per minute per admin.
    """
    ctx = get_context()

    # Build query for target users
    query = select(User.id).where(User.is_active == True)  # noqa: E712

    target_description = "all users"

    if data.target_user_ids:
        # Target specific users
        query = query.where(User.id.in_(data.target_user_ids))
        target_description = f"{len(data.target_user_ids)} specific users"

    elif data.target_plan_id:
        # Target users with specific plan
        query = (
            select(User.id)
            .join(Subscription, Subscription.user_id == User.id)
            .where(
                User.is_active == True,  # noqa: E712
                Subscription.plan_id == data.target_plan_id,
                Subscription.status == SubscriptionStatus.ACTIVE,
            )
        )
        # Get plan name for audit
        plan_result = await db.execute(
            select(Plan.display_name).where(Plan.id == data.target_plan_id)
        )
        plan_name = plan_result.scalar_one_or_none() or "Unknown"
        target_description = f"users with {plan_name} plan"

    # Get user IDs
    result = await db.execute(query)
    user_ids = [row[0] for row in result.all()]

    if not user_ids:
        raise HTTPException(
            status_code=400,
            detail="No users match the target criteria",
        )

    # Rate limiting: Check recent broadcasts from this admin
    recent_broadcast_check = await db.execute(
        select(func.count(Notification.id))
        .where(
            Notification.type == NotificationType.SYSTEM_ANNOUNCEMENT.value,
            Notification.created_at >= datetime.utcnow() - timedelta(minutes=1),
        )
        .limit(1)
    )
    recent_count = recent_broadcast_check.scalar() or 0

    # Allow max 1000 notifications per minute to prevent spam
    if recent_count > 1000:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please wait before sending more notifications.",
        )

    # Create notifications
    count = await notification_service.create_bulk_notifications(
        db=db,
        user_ids=user_ids,
        type=data.type,
        category=data.category,
        title=data.title,
        message=data.message,
        priority=data.priority,
        action_url=data.action_url,
        expires_at=data.expires_at,
    )

    # Create audit log
    await audit_service.create_audit_log(
        db=db,
        admin_id=admin.id,
        action="notification_broadcast",
        description=f"Broadcast notification '{data.title}' to {target_description} ({count} users)",
        target_type="notification",
        details={
            "title": data.title,
            "message": data.message[:200],  # Truncate for log
            "type": data.type.value,
            "category": data.category.value,
            "priority": data.priority.value,
            "target_plan_id": str(data.target_plan_id) if data.target_plan_id else None,
            "target_user_count": len(data.target_user_ids) if data.target_user_ids else None,
            "notifications_created": count,
        },
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    await db.commit()

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=BroadcastNotificationResponse(
            success=True,
            notifications_created=count,
            message=f"Successfully sent notification to {count} users",
        ),
    )


# ============================================================================
# Send to Specific Users Endpoint
# ============================================================================


@router.post("/send")
async def send_notification_to_users(
    data: SendNotificationRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> BaseResponse[SendNotificationResponse]:
    """
    Send a notification to specific users by their IDs.

    This endpoint is useful for targeted notifications to a known list of users.
    """
    ctx = get_context()

    if not data.user_ids:
        raise HTTPException(
            status_code=400,
            detail="At least one user_id is required",
        )

    if len(data.user_ids) > 100:
        raise HTTPException(
            status_code=400,
            detail="Maximum 100 users per request. Use broadcast for larger groups.",
        )

    # Verify users exist and are active
    result = await db.execute(
        select(User.id).where(
            User.id.in_(data.user_ids),
            User.is_active == True,  # noqa: E712
        )
    )
    valid_user_ids = [row[0] for row in result.all()]
    failed_user_ids = [uid for uid in data.user_ids if uid not in valid_user_ids]

    if not valid_user_ids:
        raise HTTPException(
            status_code=400,
            detail="No valid active users found in the provided list",
        )

    # Map priority string to enum
    from app.models.notification import NotificationPriority
    priority_map = {
        "low": NotificationPriority.LOW,
        "medium": NotificationPriority.MEDIUM,
        "high": NotificationPriority.HIGH,
        "critical": NotificationPriority.CRITICAL,
    }
    priority = priority_map.get(data.priority.lower(), NotificationPriority.MEDIUM)

    # Create notifications
    count = await notification_service.create_bulk_notifications(
        db=db,
        user_ids=valid_user_ids,
        type=data.type,
        category=data.category,
        title=data.title,
        message=data.message,
        priority=priority,
        action_url=data.action_url,
        expires_at=data.expires_at,
    )

    # Create audit log
    await audit_service.create_audit_log(
        db=db,
        admin_id=admin.id,
        action="notification_send",
        description=f"Sent notification '{data.title}' to {count} users",
        target_type="notification",
        details={
            "title": data.title,
            "message": data.message[:200],
            "type": data.type.value,
            "category": data.category.value,
            "priority": data.priority,
            "target_user_ids": [str(uid) for uid in data.user_ids[:10]],  # Log first 10
            "notifications_created": count,
            "failed_user_ids": [str(uid) for uid in failed_user_ids],
        },
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    await db.commit()

    message = f"Successfully sent notification to {count} users"
    if failed_user_ids:
        message += f". {len(failed_user_ids)} users were not found or inactive."

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=SendNotificationResponse(
            success=True,
            notifications_created=count,
            failed_user_ids=failed_user_ids,
            message=message,
        ),
    )


# ============================================================================
# Recent Notifications (Admin View)
# ============================================================================


@router.get("/recent")
async def get_recent_notifications(
    page: int = 1,
    per_page: int = 20,
    category: str | None = None,
    notification_type: str | None = None,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> BaseResponse[dict]:
    """
    Get recent notifications across all users (admin view).

    Useful for monitoring notification activity.
    """
    ctx = get_context()

    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 20

    # Build query
    query = select(Notification)

    if category:
        query = query.where(Notification.category == category)
    if notification_type:
        query = query.where(Notification.type == notification_type)

    # Count total
    count_query = select(func.count(Notification.id))
    if category:
        count_query = count_query.where(Notification.category == category)
    if notification_type:
        count_query = count_query.where(Notification.type == notification_type)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated results
    offset = (page - 1) * per_page
    query = query.order_by(Notification.created_at.desc()).offset(offset).limit(per_page)

    result = await db.execute(query)
    notifications = list(result.scalars().all())

    pages = notification_service.calculate_pages(total, per_page)

    return BaseResponse(
        trace_id=ctx.trace_id,
        data={
            "items": [NotificationResponse.model_validate(n) for n in notifications],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        },
    )
