"""
DevOps Agent — Webhook Routes
"""

import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException
from config.logging_config import get_logger
from config.settings import settings

router = APIRouter()
logger = get_logger(__name__)


@router.post("/github")
async def github_webhook(request: Request):
    """Handle GitHub webhook events (push, PR, CI failure)."""
    body = await request.json()
    event_type = request.headers.get("X-GitHub-Event", "unknown")

    logger.info("GitHub webhook received", event=event_type)

    if event_type == "push":
        return {"status": "received", "action": "CI pipeline triggered", "event": event_type}
    elif event_type == "pull_request":
        return {"status": "received", "action": "PR analysis queued", "event": event_type}
    elif event_type == "check_run":
        return {"status": "received", "action": "CI failure investigation queued", "event": event_type}

    return {"status": "received", "event": event_type}


@router.post("/alertmanager")
async def alertmanager_webhook(request: Request):
    """Handle Prometheus Alertmanager webhook events."""
    body = await request.json()
    alerts = body.get("alerts", [])

    logger.info("Alertmanager webhook received", alert_count=len(alerts))

    return {
        "status": "received",
        "alerts_processed": len(alerts),
        "action": "Incident response agent dispatched",
    }


@router.post("/custom")
async def custom_webhook(request: Request):
    """Handle custom event webhooks."""
    body = await request.json()
    event_type = body.get("event_type", "unknown")

    logger.info("Custom webhook received", event=event_type)

    return {"status": "received", "event_type": event_type, "action": "Event queued for processing"}
