"""LiteLLM Key Management Service.

This service manages virtual keys in LiteLLM for subscription-based access control.
"""

import logging
import uuid
from datetime import datetime
from typing import Any

import httpx

from app.config import settings
from app.core.telemetry import traced
from app.models.plan import Plan

logger = logging.getLogger(__name__)


class LiteLLMKeyError(Exception):
    """Exception for LiteLLM key management errors."""

    pass


@traced()
async def create_virtual_key(
    user_id: uuid.UUID,
    plan: Plan,
    user_email: str,
    team_id: str | None = None,
) -> dict[str, Any]:
    """
    Create a virtual key in LiteLLM for a user subscription.

    Args:
        user_id: The user's ID
        plan: The subscription plan
        user_email: User's email for identification
        team_id: Optional team ID

    Returns:
        Dict containing key_id and api_key
    """
    if not settings.litellm_api_key:
        logger.warning("LiteLLM API key not configured, skipping key creation")
        return {"key_id": None, "api_key": None}

    url = f"{settings.litellm_api_url}/key/generate"

    payload = {
        "user_id": str(user_id),
        "key_alias": f"sub_{user_id}",
        "metadata": {
            "user_email": user_email,
            "plan_id": str(plan.id),
            "plan_name": plan.name,
        },
        "models": plan.allowed_models if plan.allowed_models else [],
        "max_budget": None,  # Use token limits instead
        "tpm_limit": None,  # Tokens per minute - let LiteLLM handle via RPM
        "rpm_limit": plan.requests_per_minute,
        "max_parallel_requests": max(1, plan.requests_per_minute // 2),
    }

    if team_id:
        payload["team_id"] = team_id

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {settings.litellm_api_key}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()

            logger.info(f"Created LiteLLM key for user {user_id}: {data.get('key_name')}")

            return {
                "key_id": data.get("key"),  # This is the key ID
                "api_key": data.get("key"),  # The actual API key
                "token": data.get("token"),  # Alternative field name
            }

    except httpx.HTTPStatusError as e:
        logger.error(f"LiteLLM API error: {e.response.status_code} - {e.response.text}")
        raise LiteLLMKeyError(f"Failed to create key: {e.response.text}") from e
    except httpx.RequestError as e:
        logger.error(f"LiteLLM connection error: {e}")
        raise LiteLLMKeyError(f"Failed to connect to LiteLLM: {e}") from e


@traced()
async def update_virtual_key(
    key_id: str,
    plan: Plan,
) -> bool:
    """
    Update a virtual key in LiteLLM with new plan limits.

    Args:
        key_id: The LiteLLM key ID
        plan: The new plan with updated limits

    Returns:
        True if successful
    """
    if not settings.litellm_api_key or not key_id:
        logger.warning("LiteLLM not configured or no key_id, skipping key update")
        return False

    url = f"{settings.litellm_api_url}/key/update"

    payload = {
        "key": key_id,
        "models": plan.allowed_models if plan.allowed_models else [],
        "rpm_limit": plan.requests_per_minute,
        "max_parallel_requests": max(1, plan.requests_per_minute // 2),
        "metadata": {
            "plan_id": str(plan.id),
            "plan_name": plan.name,
            "updated_at": datetime.utcnow().isoformat(),
        },
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {settings.litellm_api_key}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
            response.raise_for_status()

            logger.info(f"Updated LiteLLM key {key_id}")
            return True

    except httpx.HTTPStatusError as e:
        logger.error(f"LiteLLM API error: {e.response.status_code} - {e.response.text}")
        raise LiteLLMKeyError(f"Failed to update key: {e.response.text}") from e
    except httpx.RequestError as e:
        logger.error(f"LiteLLM connection error: {e}")
        raise LiteLLMKeyError(f"Failed to connect to LiteLLM: {e}") from e


@traced()
async def delete_virtual_key(key_id: str) -> bool:
    """
    Delete a virtual key in LiteLLM.

    Args:
        key_id: The LiteLLM key ID

    Returns:
        True if successful
    """
    if not settings.litellm_api_key or not key_id:
        logger.warning("LiteLLM not configured or no key_id, skipping key deletion")
        return False

    url = f"{settings.litellm_api_url}/key/delete"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={"keys": [key_id]},
                headers={
                    "Authorization": f"Bearer {settings.litellm_api_key}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
            response.raise_for_status()

            logger.info(f"Deleted LiteLLM key {key_id}")
            return True

    except httpx.HTTPStatusError as e:
        logger.error(f"LiteLLM API error: {e.response.status_code} - {e.response.text}")
        raise LiteLLMKeyError(f"Failed to delete key: {e.response.text}") from e
    except httpx.RequestError as e:
        logger.error(f"LiteLLM connection error: {e}")
        raise LiteLLMKeyError(f"Failed to connect to LiteLLM: {e}") from e


@traced()
async def get_key_info(key_id: str) -> dict[str, Any] | None:
    """
    Get information about a virtual key.

    Args:
        key_id: The LiteLLM key ID

    Returns:
        Key information or None if not found
    """
    if not settings.litellm_api_key or not key_id:
        return None

    url = f"{settings.litellm_api_url}/key/info"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params={"key": key_id},
                headers={
                    "Authorization": f"Bearer {settings.litellm_api_key}",
                },
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        logger.error(f"LiteLLM API error: {e.response.status_code}")
        return None
    except httpx.RequestError as e:
        logger.error(f"LiteLLM connection error: {e}")
        return None


@traced()
async def disable_virtual_key(key_id: str) -> bool:
    """
    Disable a virtual key (for canceled subscriptions).

    Args:
        key_id: The LiteLLM key ID

    Returns:
        True if successful
    """
    if not settings.litellm_api_key or not key_id:
        return False

    url = f"{settings.litellm_api_url}/key/update"

    payload = {
        "key": key_id,
        "models": [],  # Remove all model access
        "rpm_limit": 0,
        "max_parallel_requests": 0,
        "metadata": {
            "disabled": True,
            "disabled_at": datetime.utcnow().isoformat(),
        },
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {settings.litellm_api_key}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
            response.raise_for_status()

            logger.info(f"Disabled LiteLLM key {key_id}")
            return True

    except httpx.HTTPStatusError as e:
        logger.error(f"LiteLLM API error: {e.response.status_code}")
        return False
    except httpx.RequestError as e:
        logger.error(f"LiteLLM connection error: {e}")
        return False
