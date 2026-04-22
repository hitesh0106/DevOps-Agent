"""Pydantic schemas for Pipeline endpoints."""

from pydantic import BaseModel, Field
from typing import Optional


class PipelineCreate(BaseModel):
    name: str
    repo: str
    trigger: str = "manual"


class PipelineTrigger(BaseModel):
    pipeline_id: str
    branch: str = Field(default="main")
    params: Optional[dict] = None


class PipelineResponse(BaseModel):
    id: str
    name: str
    repo: str
    status: str
    last_run: Optional[str] = None

    class Config:
        from_attributes = True
