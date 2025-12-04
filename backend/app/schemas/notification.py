"""Notification schemas for API requests/responses."""

import uuid
from datetime import datetime, time

from pydantic import BaseModel, ConfigDict

from app.models.notification import (
    NotificationCategory,
    NotificationPriority,
    NotificationType,
)


# Notification schemas
class NotificationCreate(BaseModel):
    """Schema for creating a notification."""

    user_id: uuid.UUID
    type: NotificationType
    category: NotificationCategory
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.LOW
    action_url: str | None = None
    extra_data: dict | None = None
    expires_at: datetime | None = None


class NotificationResponse(BaseModel):
    """Single notification response."""

    id: uuid.UUID
    user_id: uuid.UUID
    type: str
    category: str
    title: str
    message: str
    priority: str
    read_at: datetime | None
    action_url: str | None
    extra_data: dict | None
    expires_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    """Paginated notification list response."""

    items: list[NotificationResponse]
    total: int
    page: int
    per_page: int
    pages: int


class UnreadCountResponse(BaseModel):
    """Unread notification count for badge."""

    count: int


class MarkAsReadResponse(BaseModel):
    """Response for marking notification as read."""

    success: bool
    read_at: datetime


class MarkAllAsReadResponse(BaseModel):
    """Response for marking all notifications as read."""

    success: bool
    count: int


# Notification Preference schemas
class CategorySetting(BaseModel):
    """Per-category notification setting."""

    email: bool = True
    in_app: bool = True


class CategorySettings(BaseModel):
    """All category settings."""

    billing: CategorySetting = CategorySetting()
    document: CategorySetting = CategorySetting(email=False)
    system: CategorySetting = CategorySetting()
    account: CategorySetting = CategorySetting()


class NotificationPreferenceUpdate(BaseModel):
    """Schema for updating notification preferences."""

    email_enabled: bool | None = None
    in_app_enabled: bool | None = None
    category_settings: dict | None = None
    quiet_hours_start: time | None = None
    quiet_hours_end: time | None = None


class NotificationPreferenceResponse(BaseModel):
    """Notification preference response."""

    id: uuid.UUID
    user_id: uuid.UUID
    email_enabled: bool
    in_app_enabled: bool
    category_settings: dict
    quiet_hours_start: time | None
    quiet_hours_end: time | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Admin notification schemas
class BroadcastNotificationCreate(BaseModel):
    """Schema for creating a broadcast notification to all/selected users."""

    type: NotificationType = NotificationType.SYSTEM_ANNOUNCEMENT
    category: NotificationCategory = NotificationCategory.SYSTEM
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.MEDIUM
    action_url: str | None = None
    target_plan_id: uuid.UUID | None = None  # Target specific plan subscribers
    target_user_ids: list[uuid.UUID] | None = None  # Target specific users
    expires_at: datetime | None = None


class BroadcastNotificationResponse(BaseModel):
    """Response for broadcast notification."""

    success: bool
    notifications_created: int
    message: str
