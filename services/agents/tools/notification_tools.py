"""Notification tools for MANTIS agents."""

import logging
from typing import Any

logger = logging.getLogger("mantis.agents.notifications")


async def send_email(
    to: str, subject: str, body: str, attachments: list[str] | None = None
) -> dict[str, Any]:
    """Send email notification.

    In production, integrates with SMTP or email service.
    """
    logger.info(f"Email notification: to={to}, subject={subject}")
    return {
        "status": "sent",
        "to": to,
        "subject": subject,
        "method": "email",
    }


async def send_slack_notification(
    channel: str, message: str, severity: str = "info"
) -> dict[str, Any]:
    """Send Slack notification.

    In production, uses Slack webhook URL.
    """
    emoji_map = {
        "info": "information_source",
        "warning": "warning",
        "critical": "rotating_light",
        "emergency": "sos",
    }
    logger.info(f"Slack notification: channel={channel}, severity={severity}")
    return {
        "status": "sent",
        "channel": channel,
        "severity": severity,
        "method": "slack",
    }


async def send_webhook(
    url: str, payload: dict[str, Any]
) -> dict[str, Any]:
    """Send webhook notification to external system."""
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)
            return {"status": "sent", "status_code": response.status_code}
    except Exception as e:
        logger.error(f"Webhook failed: {e}")
        return {"status": "failed", "error": str(e)}
