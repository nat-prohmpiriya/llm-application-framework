"""Subscription schemas for API request/response."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.subscription import BillingInterval, SubscriptionStatus


class SubscriptionCreate(BaseModel):
    """Schema for creating a new subscription."""

    user_id: uuid.UUID
    plan_id: uuid.UUID
    billing_interval: BillingInterval = BillingInterval.MONTHLY
    trial_days: int | None = Field(None, ge=0, le=90)


class SubscriptionUpdate(BaseModel):
    """Schema for updating a subscription."""

    status: SubscriptionStatus | None = None
    billing_interval: BillingInterval | None = None
    cancel_reason: str | None = None


class SubscriptionUpgrade(BaseModel):
    """Schema for upgrading a subscription to a new plan."""

    new_plan_id: uuid.UUID
    billing_interval: BillingInterval | None = None
    prorate: bool = True


class SubscriptionDowngrade(BaseModel):
    """Schema for downgrading a subscription to a new plan."""

    new_plan_id: uuid.UUID
    billing_interval: BillingInterval | None = None
    effective_at_period_end: bool = True


class SubscriptionCancel(BaseModel):
    """Schema for canceling a subscription."""

    cancel_reason: str | None = None
    cancel_at_period_end: bool = True


class UserSummary(BaseModel):
    """Summary of user info for subscription response."""

    id: uuid.UUID
    email: str
    username: str

    model_config = ConfigDict(from_attributes=True)


class PlanSummary(BaseModel):
    """Summary of plan info for subscription response."""

    id: uuid.UUID
    name: str
    display_name: str
    price_monthly: float
    price_yearly: float | None

    model_config = ConfigDict(from_attributes=True)


class SubscriptionResponse(BaseModel):
    """Schema for subscription response."""

    id: uuid.UUID
    user_id: uuid.UUID
    plan_id: uuid.UUID
    status: SubscriptionStatus
    billing_interval: BillingInterval

    # Dates
    start_date: datetime
    end_date: datetime | None
    trial_end_date: datetime | None
    canceled_at: datetime | None
    current_period_start: datetime | None
    current_period_end: datetime | None

    # External IDs
    stripe_subscription_id: str | None
    stripe_customer_id: str | None
    litellm_key_id: str | None
    litellm_team_id: str | None

    # Cancellation
    cancel_reason: str | None

    # Timestamps
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubscriptionDetailResponse(SubscriptionResponse):
    """Schema for subscription detail with user and plan info."""

    user: UserSummary
    plan: PlanSummary


class SubscriptionListResponse(BaseModel):
    """Schema for paginated subscription list response."""

    items: list[SubscriptionDetailResponse]
    total: int
    page: int
    per_page: int
    pages: int


class SubscriptionFilter(BaseModel):
    """Filter options for subscription list."""

    status: SubscriptionStatus | None = None
    plan_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None
