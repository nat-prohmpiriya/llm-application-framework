"""Webhook handlers for external services."""

import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.context import get_context
from app.core.dependencies import get_db
from app.models.subscription import SubscriptionStatus
from app.schemas.base import BaseResponse, MessageResponse
from app.services import subscription as subscription_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[MessageResponse]:
    """
    Handle Stripe webhook events.

    Supported events:
    - customer.subscription.created
    - customer.subscription.updated
    - customer.subscription.deleted
    - invoice.paid
    - invoice.payment_failed
    """
    ctx = get_context()

    if not settings.stripe_secret_key:
        logger.warning("Stripe not configured, ignoring webhook")
        return BaseResponse(
            trace_id=ctx.trace_id,
            data=MessageResponse(message="Stripe not configured"),
        )

    # Get raw body for signature verification
    payload = await request.body()

    try:
        import stripe

        stripe.api_key = settings.stripe_secret_key

        # Verify webhook signature
        if settings.stripe_webhook_secret and stripe_signature:
            try:
                event = stripe.Webhook.construct_event(
                    payload,
                    stripe_signature,
                    settings.stripe_webhook_secret,
                )
            except stripe.error.SignatureVerificationError as e:
                logger.error(f"Stripe signature verification failed: {e}")
                raise HTTPException(status_code=400, detail="Invalid signature") from e
        else:
            # No webhook secret configured, parse without verification (dev mode)
            import json
            event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)

        event_type = event["type"]
        data = event["data"]["object"]

        logger.info(f"Processing Stripe webhook: {event_type}")

        if event_type == "customer.subscription.created":
            await _handle_subscription_created(db, data)

        elif event_type == "customer.subscription.updated":
            await _handle_subscription_updated(db, data)

        elif event_type == "customer.subscription.deleted":
            await _handle_subscription_deleted(db, data)

        elif event_type == "invoice.paid":
            await _handle_invoice_paid(db, data)

        elif event_type == "invoice.payment_failed":
            await _handle_invoice_payment_failed(db, data)

        else:
            logger.debug(f"Unhandled Stripe event type: {event_type}")

        await db.commit()

        return BaseResponse(
            trace_id=ctx.trace_id,
            data=MessageResponse(message=f"Processed {event_type}"),
        )

    except ImportError:
        logger.error("Stripe library not installed")
        return BaseResponse(
            trace_id=ctx.trace_id,
            data=MessageResponse(message="Stripe library not installed"),
        )
    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed") from e


async def _handle_subscription_created(db: AsyncSession, data: dict) -> None:
    """Handle subscription.created event."""
    stripe_subscription_id = data.get("id")
    stripe_customer_id = data.get("customer")
    status = _map_stripe_status(data.get("status"))

    logger.info(
        f"Stripe subscription created: {stripe_subscription_id}, "
        f"customer: {stripe_customer_id}, status: {status}"
    )

    # Note: The actual subscription should be created via our API first,
    # then linked to Stripe. This webhook mainly confirms the creation.
    _ = db  # Placeholder for future use


async def _handle_subscription_updated(db: AsyncSession, data: dict) -> None:
    """Handle subscription.updated event."""
    stripe_subscription_id = data.get("id")
    status = _map_stripe_status(data.get("status"))

    current_period_start = None
    current_period_end = None

    if data.get("current_period_start"):
        current_period_start = datetime.fromtimestamp(
            data["current_period_start"], tz=UTC
        )
    if data.get("current_period_end"):
        current_period_end = datetime.fromtimestamp(
            data["current_period_end"], tz=UTC
        )

    await subscription_service.update_subscription_from_stripe(
        db=db,
        stripe_subscription_id=stripe_subscription_id,
        status=status,
        current_period_start=current_period_start,
        current_period_end=current_period_end,
    )


async def _handle_subscription_deleted(db: AsyncSession, data: dict) -> None:
    """Handle subscription.deleted event."""
    stripe_subscription_id = data.get("id")

    await subscription_service.update_subscription_from_stripe(
        db=db,
        stripe_subscription_id=stripe_subscription_id,
        status=SubscriptionStatus.CANCELED,
    )


async def _handle_invoice_paid(db: AsyncSession, data: dict) -> None:
    """Handle invoice.paid event."""
    stripe_subscription_id = data.get("subscription")

    if stripe_subscription_id:
        # Update subscription to active if it was past_due
        await subscription_service.update_subscription_from_stripe(
            db=db,
            stripe_subscription_id=stripe_subscription_id,
            status=SubscriptionStatus.ACTIVE,
        )

    logger.info(f"Invoice paid for subscription: {stripe_subscription_id}")


async def _handle_invoice_payment_failed(db: AsyncSession, data: dict) -> None:
    """Handle invoice.payment_failed event."""
    stripe_subscription_id = data.get("subscription")

    if stripe_subscription_id:
        await subscription_service.update_subscription_from_stripe(
            db=db,
            stripe_subscription_id=stripe_subscription_id,
            status=SubscriptionStatus.PAST_DUE,
        )

    logger.warning(f"Invoice payment failed for subscription: {stripe_subscription_id}")


def _map_stripe_status(stripe_status: str) -> SubscriptionStatus:
    """Map Stripe subscription status to our status."""
    status_map = {
        "active": SubscriptionStatus.ACTIVE,
        "past_due": SubscriptionStatus.PAST_DUE,
        "canceled": SubscriptionStatus.CANCELED,
        "unpaid": SubscriptionStatus.PAST_DUE,
        "trialing": SubscriptionStatus.TRIALING,
        "paused": SubscriptionStatus.PAUSED,
        "incomplete": SubscriptionStatus.PAUSED,
        "incomplete_expired": SubscriptionStatus.EXPIRED,
    }
    return status_map.get(stripe_status, SubscriptionStatus.ACTIVE)
