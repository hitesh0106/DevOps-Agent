"""
DevOps Agent — Notification Tools
"""

import json
from tools.base import BaseTool
from config.constants import ToolCategory, RiskLevel


class SendSlackMessage(BaseTool):
    name = "send_slack_message"
    description = "Send a message to a Slack channel via webhook"
    category = ToolCategory.NOTIFICATION
    risk_level = RiskLevel.LOW
    parameters_schema = '{"message": "string", "channel": "string (optional)"}'

    def execute(self, **kwargs):
        if self.simulation_mode:
            return json.dumps({"status": "sent", "channel": kwargs.get("channel", "#devops-alerts"), "message_preview": kwargs.get("message", "")[:100]})
        import httpx
        from config.settings import settings
        resp = httpx.post(settings.notifications.slack_webhook_url, json={"text": kwargs["message"], "channel": kwargs.get("channel", settings.notifications.slack_channel)})
        return json.dumps({"status": "sent" if resp.status_code == 200 else "failed", "code": resp.status_code})


class SendEmail(BaseTool):
    name = "send_email"
    description = "Send an email notification via SMTP"
    category = ToolCategory.NOTIFICATION
    risk_level = RiskLevel.LOW
    parameters_schema = '{"to": "string", "subject": "string", "body": "string"}'

    def execute(self, **kwargs):
        if self.simulation_mode:
            return json.dumps({"status": "sent", "to": kwargs.get("to", "admin@example.com"), "subject": kwargs.get("subject", "Alert")})
        import smtplib
        from email.mime.text import MIMEText
        from config.settings import settings
        msg = MIMEText(kwargs["body"])
        msg["Subject"] = kwargs["subject"]
        msg["To"] = kwargs["to"]
        msg["From"] = settings.notifications.smtp_username
        with smtplib.SMTP(settings.notifications.smtp_host, settings.notifications.smtp_port) as server:
            server.starttls()
            server.login(settings.notifications.smtp_username, settings.notifications.smtp_password)
            server.send_message(msg)
        return json.dumps({"status": "sent"})


class CreatePagerDutyIncident(BaseTool):
    name = "create_pagerduty_incident"
    description = "Create a PagerDuty incident for critical alerts"
    category = ToolCategory.NOTIFICATION
    risk_level = RiskLevel.MEDIUM
    parameters_schema = '{"title": "string", "severity": "string (critical|high|warning|info)", "details": "string"}'

    def execute(self, **kwargs):
        if self.simulation_mode:
            return json.dumps({
                "status": "created", "incident_id": "PD-2024-001",
                "title": kwargs.get("title", "Critical Alert"),
                "severity": kwargs.get("severity", "high"),
                "url": "https://pagerduty.com/incidents/PD-2024-001",
            })
        import httpx
        resp = httpx.post("https://events.pagerduty.com/v2/enqueue", json={
            "routing_key": kwargs.get("routing_key", ""),
            "event_action": "trigger",
            "payload": {"summary": kwargs["title"], "severity": kwargs.get("severity", "high"), "source": "devops-agent"},
        })
        return json.dumps(resp.json())
