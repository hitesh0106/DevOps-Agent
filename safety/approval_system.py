"""
DevOps Agent — Human-in-the-Loop Approval System
"""

import uuid
from datetime import datetime, timezone
from typing import Optional
from config.logging_config import get_logger

logger = get_logger(__name__)


class ApprovalRequest:
    """Represents a pending approval request."""

    def __init__(self, action: str, details: str, risk_level: str):
        self.id = str(uuid.uuid4())[:8]
        self.action = action
        self.details = details
        self.risk_level = risk_level
        self.status = "pending"  # pending, approved, rejected, expired
        self.created_at = datetime.now(timezone.utc)
        self.resolved_at: Optional[datetime] = None
        self.resolved_by: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id, "action": self.action, "details": self.details,
            "risk_level": self.risk_level, "status": self.status,
            "created_at": self.created_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolved_by": self.resolved_by,
        }


class ApprovalSystem:
    """
    Human-in-the-loop approval system for high-risk operations.
    Queues dangerous actions for manual review before execution.
    """

    def __init__(self):
        self._pending: dict[str, ApprovalRequest] = {}
        self._history: list[ApprovalRequest] = []

    def request_approval(self, action: str, details: str, risk_level: str = "high") -> ApprovalRequest:
        """Create a new approval request."""
        req = ApprovalRequest(action, details, risk_level)
        self._pending[req.id] = req
        logger.info("Approval requested", request_id=req.id, action=action)
        return req

    def approve(self, request_id: str, approved_by: str = "admin") -> bool:
        """Approve a pending request."""
        if request_id not in self._pending:
            return False
        req = self._pending.pop(request_id)
        req.status = "approved"
        req.resolved_at = datetime.now(timezone.utc)
        req.resolved_by = approved_by
        self._history.append(req)
        logger.info("Request approved", request_id=request_id, by=approved_by)
        return True

    def reject(self, request_id: str, rejected_by: str = "admin") -> bool:
        """Reject a pending request."""
        if request_id not in self._pending:
            return False
        req = self._pending.pop(request_id)
        req.status = "rejected"
        req.resolved_at = datetime.now(timezone.utc)
        req.resolved_by = rejected_by
        self._history.append(req)
        logger.info("Request rejected", request_id=request_id, by=rejected_by)
        return True

    def get_pending(self) -> list[dict]:
        """Get all pending approval requests."""
        return [r.to_dict() for r in self._pending.values()]

    def get_history(self) -> list[dict]:
        """Get approval history."""
        return [r.to_dict() for r in self._history]
