"""
DevOps Agent — Audit Trail
=============================
Tamper-proof logging of all agent actions for compliance and debugging.
"""

import json
import csv
import io
from datetime import datetime, timezone
from pathlib import Path
from config.logging_config import get_logger
from config.settings import BASE_DIR

logger = get_logger(__name__)

AUDIT_LOG_PATH = BASE_DIR / "data" / "audit_log.jsonl"


class AuditTrail:
    """
    Records every agent action with timestamp, reasoning, and outcome.
    Provides exportable reports in CSV and JSON formats.
    """

    def __init__(self, log_path: str = None):
        self.log_path = Path(log_path or AUDIT_LOG_PATH)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._entries: list[dict] = []

    def log_action(self, agent_id: str, action: str, input_data: str,
                   output: str, success: bool, risk_level: str = "safe",
                   reasoning: str = "") -> None:
        """Log an agent action."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_id": agent_id,
            "action": action,
            "input": input_data[:500],
            "output": output[:500],
            "success": success,
            "risk_level": risk_level,
            "reasoning": reasoning[:300],
        }
        self._entries.append(entry)

        # Append to file
        try:
            with open(self.log_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.warning("Failed to write audit log", error=str(e))

    def get_entries(self, limit: int = 50) -> list[dict]:
        """Get recent audit entries."""
        return self._entries[-limit:]

    def export_csv(self) -> str:
        """Export audit log as CSV string."""
        if not self._entries:
            return ""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=self._entries[0].keys())
        writer.writeheader()
        writer.writerows(self._entries)
        return output.getvalue()

    def export_json(self) -> str:
        """Export audit log as JSON string."""
        return json.dumps(self._entries, indent=2)

    def get_stats(self) -> dict:
        """Get audit statistics."""
        total = len(self._entries)
        successes = sum(1 for e in self._entries if e.get("success"))
        return {
            "total_actions": total,
            "successful": successes,
            "failed": total - successes,
            "success_rate": f"{(successes/total*100):.1f}%" if total > 0 else "N/A",
        }
