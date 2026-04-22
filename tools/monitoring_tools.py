"""
DevOps Agent — Monitoring Tools
"""

import json
from tools.base import BaseTool
from config.constants import ToolCategory, RiskLevel, SIMULATION_RESPONSES


class QueryPrometheus(BaseTool):
    name = "query_prometheus"
    description = "Execute a PromQL query against Prometheus"
    category = ToolCategory.MONITORING
    risk_level = RiskLevel.SAFE
    parameters_schema = '{"query": "string", "description": "string (optional)"}'

    def execute(self, **kwargs):
        if self.simulation_mode:
            return json.dumps({
                "query": kwargs.get("query", "up"),
                "result": SIMULATION_RESPONSES["prometheus"],
                "status": "success",
            })
        import httpx
        from config.settings import settings
        resp = httpx.get(f"{settings.monitoring.prometheus_url}/api/v1/query", params={"query": kwargs["query"]})
        return json.dumps(resp.json())


class GetAlerts(BaseTool):
    name = "get_alerts"
    description = "Fetch active alerts from Alertmanager"
    category = ToolCategory.MONITORING
    risk_level = RiskLevel.SAFE
    parameters_schema = '{}'

    def execute(self, **kwargs):
        if self.simulation_mode:
            return json.dumps({
                "active_alerts": 1,
                "alerts": [
                    {"alertname": "HighMemoryUsage", "severity": "warning", "instance": "node-3", "value": "78%", "duration": "15m"},
                ],
            })
        import httpx
        from config.settings import settings
        resp = httpx.get(f"{settings.monitoring.alertmanager_url}/api/v2/alerts")
        return json.dumps(resp.json())


class GetGrafanaDashboard(BaseTool):
    name = "get_grafana_dashboard"
    description = "Retrieve Grafana dashboard data"
    category = ToolCategory.MONITORING
    risk_level = RiskLevel.SAFE
    parameters_schema = '{"dashboard_uid": "string (optional)"}'

    def execute(self, **kwargs):
        if self.simulation_mode:
            return json.dumps({
                "dashboard": "DevOps Agent Overview",
                "panels": ["CPU Usage", "Memory Usage", "Request Rate", "Error Rate", "Deployment Frequency"],
                "last_updated": "2 minutes ago",
            })
        import httpx
        from config.settings import settings
        uid = kwargs.get("dashboard_uid", "devops-agent")
        resp = httpx.get(f"{settings.monitoring.grafana_url}/api/dashboards/uid/{uid}", headers={"Authorization": f"Bearer {settings.monitoring.grafana_api_key}"})
        return json.dumps(resp.json())


class CheckServiceHealth(BaseTool):
    name = "check_service_health"
    description = "Perform HTTP health checks on services"
    category = ToolCategory.MONITORING
    risk_level = RiskLevel.SAFE
    parameters_schema = '{"service": "string", "url": "string (optional)"}'

    def execute(self, **kwargs):
        if self.simulation_mode:
            service = kwargs.get("service", "all")
            return json.dumps({
                "service": service,
                "checks": [
                    {"name": "api-server", "url": "http://api:8000/health", "status": 200, "latency_ms": 12, "healthy": True},
                    {"name": "database", "url": "postgresql://db:5432", "status": "connected", "latency_ms": 3, "healthy": True},
                    {"name": "redis", "url": "redis://redis:6379", "status": "connected", "latency_ms": 1, "healthy": True},
                    {"name": "prometheus", "url": "http://prometheus:9090", "status": 200, "latency_ms": 8, "healthy": True},
                ],
                "overall": "healthy",
            })
        import httpx
        url = kwargs.get("url", f"http://localhost:8000/health")
        try:
            resp = httpx.get(url, timeout=10)
            return json.dumps({"status": resp.status_code, "healthy": resp.status_code == 200, "latency_ms": resp.elapsed.total_seconds() * 1000})
        except Exception as e:
            return json.dumps({"status": "error", "healthy": False, "error": str(e)})
