"""
Fires an email + a WhatsApp message to you whenever a new booking comes in.

Both are best-effort: if a channel isn't configured (or the send fails),
we log it and move on rather than breaking the booking itself. The booking
is already saved in Postgres before these are ever called.
"""

import logging

import httpx

from app.config import settings
from app.models import Booking, Zone

logger = logging.getLogger("notifications")


def _location_line(booking: Booking) -> str:
    if booking.location_shared and booking.latitude is not None and booking.longitude is not None:
        maps_link = f"https://www.google.com/maps?q={booking.latitude},{booking.longitude}"
        return f"{booking.latitude}, {booking.longitude} ({maps_link})"
    return "Not shared — use the doorstep address below"

def _build_message(booking: Booking, zone: Zone | None) -> str:
    zone_line = f"{zone.name} (~{zone.eta_minutes} min ETA)" if zone else "Not specified"
    return (
        f"New Booking Request — BagMech Bengaluru\n\n"
        f"Name: {booking.name}\n"
        f"Phone: {booking.phone}\n"
        f"Zone: {zone_line}\n"
        f"Location: {_location_line(booking)}\n"
        f"Doorstep Address: {booking.address}\n"
        f"What needs repair: {booking.issue}\n\n"
        f"Booking ID: {booking.id}"
    )

async def send_email_notification(booking: Booking, zone: Zone | None) -> None:
    if not settings.enable_email_notifications:
        return
    if not (settings.resend_api_key and settings.notify_email_to):
        logger.warning("Email notifications enabled but Resend settings incomplete — skipping.")
        return

    payload = {
        "from": settings.notify_email_from,
        "to": [settings.notify_email_to],
        "subject": f"New booking: {booking.issue} — {zone.name if zone else 'Bengaluru'}",
        "text": _build_message(booking, zone),
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                "https://api.resend.com/emails",
                json=payload,
                headers={"Authorization": f"Bearer {settings.resend_api_key}"},
            )
            resp.raise_for_status()
    except Exception:
        logger.exception("Failed to send booking email notification")


async def send_whatsapp_notification(booking: Booking, zone: Zone | None) -> None:
    if not settings.enable_whatsapp_notifications:
        return
    if not (settings.twilio_account_sid and settings.twilio_auth_token
            and settings.twilio_whatsapp_from and settings.owner_whatsapp_number):
        logger.warning("WhatsApp notifications enabled but Twilio settings incomplete — skipping.")
        return

    url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.twilio_account_sid}/Messages.json"
    data = {
        "From": f"whatsapp:{settings.twilio_whatsapp_from}",
        "To": f"whatsapp:{settings.owner_whatsapp_number}",
        "Body": _build_message(booking, zone),
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                url, data=data, auth=(settings.twilio_account_sid, settings.twilio_auth_token)
            )
            resp.raise_for_status()
    except Exception:
        logger.exception("Failed to send booking WhatsApp notification")


async def notify_new_booking(booking: Booking, zone: Zone | None) -> None:
    """Call both channels; each fails independently without blocking the other."""
    await send_email_notification(booking, zone)
    await send_whatsapp_notification(booking, zone)