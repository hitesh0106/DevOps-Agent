"""Pydantic schemas for Webhook endpoints."""

from pydantic import BaseModel
from typing import Optional


class GitHubWebhookPayload(BaseModel):
    action: Optional[str] = None
    repository: Optional[dict] = None
    sender: Optional[dict] = None


class AlertManagerPayload(BaseModel):
    status: str = "firing"
    alerts: list = []


class CustomWebhookPayload(BaseModel):
    event_type: str
    data: Optional[dict] = None
    source: Optional[str] = None
