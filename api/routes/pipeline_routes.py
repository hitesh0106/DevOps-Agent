"""
DevOps Agent — Pipeline Routes
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter()

# In-memory pipeline store (simulation)
PIPELINES = [
    {"id": "pipe-001", "name": "CI Pipeline", "repo": "frontend-app", "status": "success", "last_run": "2h ago", "duration": "4m 23s", "trigger": "push"},
    {"id": "pipe-002", "name": "CD Pipeline", "repo": "backend-api", "status": "success", "last_run": "1h ago", "duration": "6m 12s", "trigger": "merge"},
    {"id": "pipe-003", "name": "Security Scan", "repo": "infra-config", "status": "running", "last_run": "now", "duration": "2m 45s", "trigger": "schedule"},
]


class PipelineTrigger(BaseModel):
    pipeline_id: str
    branch: str = Field(default="main")
    params: Optional[dict] = None


@router.get("/")
async def list_pipelines():
    """List all CI/CD pipelines."""
    return {"pipelines": PIPELINES, "total": len(PIPELINES)}


@router.get("/{pipeline_id}")
async def get_pipeline(pipeline_id: str):
    """Get pipeline details."""
    for p in PIPELINES:
        if p["id"] == pipeline_id:
            return p
    return {"error": "Pipeline not found"}


@router.post("/trigger")
async def trigger_pipeline(request: PipelineTrigger):
    """Trigger a pipeline run."""
    return {
        "status": "triggered",
        "pipeline_id": request.pipeline_id,
        "branch": request.branch,
        "run_id": "run-2024-042",
        "message": "Pipeline execution started",
    }
