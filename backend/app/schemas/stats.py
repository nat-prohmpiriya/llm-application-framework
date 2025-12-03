"""Statistics schemas."""

from pydantic import BaseModel


class UserStatsResponse(BaseModel):
    """Schema for user usage statistics."""

    conversations_count: int
    documents_count: int
    agents_count: int
    total_messages: int
