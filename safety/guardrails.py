"""
DevOps Agent — Safety Guardrails
===================================
Validates agent actions against safety rules to prevent destructive operations.
"""

import re
from datetime import datetime, timezone
from config.logging_config import get_logger
from config.constants import BLOCKED_COMMANDS, APPROVAL_REQUIRED_PATTERNS, RiskLevel

logger = get_logger(__name__)


class SafetyGuardrails:
    """
    Safety guardrails for agent actions.

    Checks every action before execution:
    - Blocks known dangerous commands
    - Flags operations requiring human approval
    - Logs all actions for audit trail
    """

    def __init__(self):
        self.blocked_commands = BLOCKED_COMMANDS
        self.approval_patterns = APPROVAL_REQUIRED_PATTERNS
        self.action_log: list[dict] = []

    def check_action(self, action_name: str, action_input: str) -> dict:
        """
        Validate an action against safety rules.

        Returns:
            dict with keys: allowed (bool), reason (str), risk_level (str)
        """
        # Log the action
        log_entry = {
            "action": action_name,
            "input": action_input[:200],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Check blocked commands
        input_lower = action_input.lower()
        for blocked in self.blocked_commands:
            if blocked.lower() in input_lower:
                log_entry["result"] = "BLOCKED"
                log_entry["reason"] = f"Dangerous command: {blocked}"
                self.action_log.append(log_entry)
                logger.warning("Action BLOCKED", action=action_name, reason=blocked)
                return {
                    "allowed": False,
                    "reason": f"Blocked: '{blocked}' is a dangerous command",
                    "risk_level": RiskLevel.CRITICAL.value,
                }

        # Check approval-required patterns
        for pattern in self.approval_patterns:
            if pattern.lower() in input_lower:
                log_entry["result"] = "NEEDS_APPROVAL"
                log_entry["reason"] = f"Requires approval: {pattern}"
                self.action_log.append(log_entry)
                logger.info("Action needs approval", action=action_name, pattern=pattern)
                # In simulation mode, auto-approve
                return {
                    "allowed": True,
                    "reason": f"⚠️ High-risk operation ({pattern}) — auto-approved in simulation mode",
                    "risk_level": RiskLevel.HIGH.value,
                }

        # Action is allowed
        log_entry["result"] = "ALLOWED"
        self.action_log.append(log_entry)
        return {
            "allowed": True,
            "reason": "Action passes safety checks",
            "risk_level": RiskLevel.SAFE.value,
        }

    def get_audit_log(self) -> list[dict]:
        """Return the full action audit log."""
        return self.action_log

    def get_blocked_count(self) -> int:
        """Return number of blocked actions."""
        return sum(1 for entry in self.action_log if entry.get("result") == "BLOCKED")
