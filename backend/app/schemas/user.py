import re
import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator


class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    username: str
    password: str
    first_name: str | None = None
    last_name: str | None = None


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if len(v) < 3 or len(v) > 50:
            raise ValueError("Username must be between 3 and 50 characters")
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username can only contain alphanumeric characters and underscores")
        return v


class UserResponse(BaseModel):
    """Schema for user response."""

    id: uuid.UUID
    email: str
    username: str
    first_name: str | None
    last_name: str | None
    is_active: bool
    tier: str

    model_config = {"from_attributes": True}


class UserProfileResponse(BaseModel):
    """Schema for user profile response with timestamps."""

    id: uuid.UUID
    email: str
    username: str
    first_name: str | None
    last_name: str | None
    is_active: bool
    tier: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChangePasswordRequest(BaseModel):
    """Schema for changing user password."""

    current_password: str
    new_password: str
    confirm_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("confirm_password")
    @classmethod
    def validate_confirm_password(cls, v: str, info) -> str:
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v


class DeleteAccountRequest(BaseModel):
    """Schema for deleting user account."""

    password: str
    confirmation: str

    @field_validator("confirmation")
    @classmethod
    def validate_confirmation(cls, v: str) -> str:
        if v != "DELETE":
            raise ValueError("Confirmation must be 'DELETE'")
        return v
