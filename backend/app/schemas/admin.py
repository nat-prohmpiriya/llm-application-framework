"""Admin dashboard schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserStats(BaseModel):
    """User statistics."""

    total_users: int
    active_today: int
    new_this_week: int
    new_this_month: int


class UsageStats(BaseModel):
    """Usage statistics from LiteLLM."""

    requests_today: int
    requests_this_month: int
    tokens_today: int
    tokens_this_month: int
    cost_today: float
    cost_this_month: float


class RevenueStats(BaseModel):
    """Revenue statistics."""

    mrr: float  # Monthly Recurring Revenue
    arr: float  # Annual Recurring Revenue
    total_revenue: float
    revenue_this_month: float


class PlanSubscriberCount(BaseModel):
    """Subscriber count per plan."""

    plan_id: str
    plan_name: str
    display_name: str
    subscriber_count: int
    percentage: float

    model_config = ConfigDict(from_attributes=True)


class DailyUsage(BaseModel):
    """Daily usage data point for charts."""

    date: str  # ISO date string
    requests: int
    tokens: int
    cost: float


class DashboardStats(BaseModel):
    """Complete dashboard statistics."""

    users: UserStats
    usage: UsageStats
    revenue: RevenueStats
    subscribers_by_plan: list[PlanSubscriberCount]
    usage_over_time: list[DailyUsage]
