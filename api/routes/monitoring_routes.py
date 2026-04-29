"""
DevOps Agent — Monitoring Routes
Full CRUD support for incidents + monitoring metrics.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from config.constants import SIMULATION_RESPONSES
import uuid
from datetime import datetime

router = APIRouter()

# In-memory incidents store
INCIDENTS = [
    {"id": "INC-001", "title": "API latency spike", "severity": "warning", "status": "resolved", "resolved_by": "agent", "duration": "8m", "description": "API response time exceeded 2s threshold", "created_at": "2026-04-23T08:00:00"},
    {"id": "INC-002", "title": "Pod CrashLoopBackOff", "severity": "critical", "status": "resolved", "resolved_by": "agent", "duration": "3m", "description": "Pod payment-service-7d crashed repeatedly", "created_at": "2026-04-23T09:00:00"},
    {"id": "INC-003", "title": "High memory on node-3", "severity": "critical", "status": "open", "resolved_by": "—", "duration": "15m", "description": "Memory usage exceeded 85% on node-3", "created_at": "2026-04-23T09:10:00"},
]

# Auto-increment counter
_incident_counter = 4


class IncidentCreate(BaseModel):
    title: str = Field(..., description="Incident title")
    severity: str = Field(default="warning", description="Severity: info, warning, critical")
    description: str = Field(default="", description="Incident description")


class IncidentUpdate(BaseModel):
    status: Optional[str] = Field(None, description="Status: open, investigating, resolved")
    resolved_by: Optional[str] = Field(None, description="Who resolved it")


# In-memory custom tools store
CUSTOM_TOOLS = [
    {"id": "tool-001", "name": "GitHub", "type": "integration", "status": "connected", "icon": "fa-brands fa-github", "config": {"webhook": True}},
    {"id": "tool-002", "name": "Kubernetes", "type": "integration", "status": "connected", "icon": "fa-solid fa-dharmachakra", "config": {"cluster": "production"}},
    {"id": "tool-003", "name": "Docker", "type": "integration", "status": "connected", "icon": "fa-brands fa-docker", "config": {"registry": "ghcr.io"}},
    {"id": "tool-004", "name": "Slack", "type": "notification", "status": "not_set", "icon": "fa-brands fa-slack", "config": {}},
    {"id": "tool-005", "name": "PagerDuty", "type": "notification", "status": "not_set", "icon": "fa-solid fa-bell", "config": {}},
]


class CustomToolCreate(BaseModel):
    name: str = Field(..., description="Tool name")
    type: str = Field(default="integration", description="Type: integration, notification, monitoring, custom")
    config: Optional[dict] = Field(default={}, description="Tool configuration")


@router.get("/metrics")
async def get_metrics():
    """Get system metrics overview."""
    return {
        "cpu_usage": SIMULATION_RESPONSES["prometheus"]["cpu_usage"],
        "memory_usage": SIMULATION_RESPONSES["prometheus"]["memory_usage"],
        "error_rate": SIMULATION_RESPONSES["prometheus"]["error_rate"],
        "request_latency_p99": SIMULATION_RESPONSES["prometheus"]["request_latency_p99"],
        "containers_running": 4,
        "pods_active": 12,
        "nodes_ready": 3,
    }


@router.get("/alerts")
async def get_active_alerts():
    """Get active monitoring alerts."""
    return {
        "alerts": [
            {"name": "HighMemoryUsage", "severity": "warning", "instance": "node-3", "value": "78%", "active_for": "15m"},
        ],
        "total": 1,
    }


# ===== INCIDENTS CRUD =====
@router.get("/incidents")
async def get_incidents():
    """Get all incidents."""
    return {"incidents": INCIDENTS, "total": len(INCIDENTS)}


@router.post("/incidents")
async def create_incident(request: IncidentCreate):
    """Create a new incident."""
    global _incident_counter
    new_id = f"INC-{_incident_counter:03d}"
    _incident_counter += 1
    new_incident = {
        "id": new_id,
        "title": request.title,
        "severity": request.severity,
        "status": "open",
        "resolved_by": "—",
        "duration": "0m",
        "description": request.description,
        "created_at": datetime.utcnow().isoformat(),
    }
    INCIDENTS.insert(0, new_incident)  # Add to top
    return {"status": "created", "incident": new_incident}


@router.patch("/incidents/{incident_id}")
async def update_incident(incident_id: str, request: IncidentUpdate):
    """Update incident status."""
    for inc in INCIDENTS:
        if inc["id"] == incident_id:
            if request.status:
                inc["status"] = request.status
            if request.resolved_by:
                inc["resolved_by"] = request.resolved_by
            return {"status": "updated", "incident": inc}
    raise HTTPException(status_code=404, detail="Incident not found")


@router.delete("/incidents/{incident_id}")
async def delete_incident(incident_id: str):
    """Delete an incident."""
    for i, inc in enumerate(INCIDENTS):
        if inc["id"] == incident_id:
            INCIDENTS.pop(i)
            return {"status": "deleted", "incident_id": incident_id}
    raise HTTPException(status_code=404, detail="Incident not found")


# ===== CUSTOM TOOLS CRUD =====
@router.get("/tools")
async def list_custom_tools():
    """List all custom tools/integrations."""
    return {"tools": CUSTOM_TOOLS, "total": len(CUSTOM_TOOLS)}


@router.post("/tools")
async def add_custom_tool(request: CustomToolCreate):
    """Add a custom tool/integration."""
    new_id = f"tool-{str(uuid.uuid4())[:8]}"
    new_tool = {
        "id": new_id,
        "name": request.name,
        "type": request.type,
        "status": "connected",
        "icon": _get_tool_icon(request.type),
        "config": request.config or {},
    }
    CUSTOM_TOOLS.append(new_tool)
    return {"status": "created", "tool": new_tool}


@router.delete("/tools/{tool_id}")
async def delete_custom_tool(tool_id: str):
    """Remove a custom tool."""
    for i, t in enumerate(CUSTOM_TOOLS):
        if t["id"] == tool_id:
            CUSTOM_TOOLS.pop(i)
            return {"status": "deleted", "tool_id": tool_id}
    raise HTTPException(status_code=404, detail="Tool not found")


def _get_tool_icon(tool_type: str) -> str:
    """Get default icon based on tool type."""
    icons = {
        "integration": "fa-solid fa-plug",
        "notification": "fa-solid fa-bell",
        "monitoring": "fa-solid fa-chart-line",
        "custom": "fa-solid fa-puzzle-piece",
    }
    return icons.get(tool_type, "fa-solid fa-gear")
