"""
DevOps Agent — Pipeline Routes
Full CRUD support for CI/CD pipelines.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import uuid
from datetime import datetime

router = APIRouter()

# In-memory pipeline store (simulation)
PIPELINES = [
    {"id": "pipe-001", "name": "CI Pipeline", "repo": "frontend-app", "status": "success", "last_run": "2h ago", "duration": "4m 23s", "trigger": "push", "branch": "main", "created_at": "2026-04-20T10:00:00"},
    {"id": "pipe-002", "name": "CD Pipeline", "repo": "backend-api", "status": "success", "last_run": "1h ago", "duration": "6m 12s", "trigger": "merge", "branch": "main", "created_at": "2026-04-20T11:00:00"},
    {"id": "pipe-003", "name": "Security Scan", "repo": "infra-config", "status": "running", "last_run": "now", "duration": "2m 45s", "trigger": "schedule", "branch": "main", "created_at": "2026-04-20T12:00:00"},
    {"id": "pipe-004", "name": "Docker Build", "repo": "main-app", "status": "success", "last_run": "3h ago", "duration": "3m 10s", "trigger": "merge", "branch": "main", "created_at": "2026-04-21T09:00:00"},
    {"id": "pipe-005", "name": "K8s Deploy", "repo": "main-app", "status": "success", "last_run": "4h ago", "duration": "5m 33s", "trigger": "manual", "branch": "production", "created_at": "2026-04-21T10:00:00"},
    {"id": "pipe-006", "name": "Integration Tests", "repo": "backend-api", "status": "failed", "last_run": "5h ago", "duration": "8m 02s", "trigger": "push", "branch": "develop", "created_at": "2026-04-21T11:00:00"},
]


class PipelineCreate(BaseModel):
    name: str = Field(..., description="Pipeline name")
    repo: str = Field(..., description="Repository name")
    trigger: str = Field(default="push", description="Trigger type: push, merge, schedule, manual")
    branch: str = Field(default="main", description="Branch name")


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
    raise HTTPException(status_code=404, detail="Pipeline not found")


@router.post("/")
async def create_pipeline(request: PipelineCreate):
    """Create a new pipeline."""
    new_id = f"pipe-{str(uuid.uuid4())[:8]}"
    new_pipeline = {
        "id": new_id,
        "name": request.name,
        "repo": request.repo,
        "status": "pending",
        "last_run": "never",
        "duration": "—",
        "trigger": request.trigger,
        "branch": request.branch,
        "created_at": datetime.utcnow().isoformat(),
    }
    PIPELINES.append(new_pipeline)
    return {"status": "created", "pipeline": new_pipeline}


@router.delete("/{pipeline_id}")
async def delete_pipeline(pipeline_id: str):
    """Delete a pipeline."""
    for i, p in enumerate(PIPELINES):
        if p["id"] == pipeline_id:
            PIPELINES.pop(i)
            return {"status": "deleted", "pipeline_id": pipeline_id}
    raise HTTPException(status_code=404, detail="Pipeline not found")


@router.post("/trigger")
async def trigger_pipeline(request: PipelineTrigger):
    """Trigger a pipeline run."""
    for p in PIPELINES:
        if p["id"] == request.pipeline_id:
            p["status"] = "running"
            p["last_run"] = "now"
            return {
                "status": "triggered",
                "pipeline_id": request.pipeline_id,
                "branch": request.branch,
                "run_id": f"run-{str(uuid.uuid4())[:8]}",
                "message": "Pipeline execution started",
            }
    raise HTTPException(status_code=404, detail="Pipeline not found")
