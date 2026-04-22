"""
DevOps Agent — Monitoring Routes
"""

from fastapi import APIRouter
from config.constants import SIMULATION_RESPONSES

router = APIRouter()


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


@router.get("/incidents")
async def get_incidents():
    """Get recent incidents."""
    return {
        "incidents": [
            {"id": "INC-001", "title": "API latency spike", "severity": "warning", "status": "resolved", "resolved_by": "agent", "duration": "8m"},
            {"id": "INC-002", "title": "Pod CrashLoopBackOff", "severity": "critical", "status": "resolved", "resolved_by": "agent", "duration": "3m"},
        ],
        "total": 2,
    }
