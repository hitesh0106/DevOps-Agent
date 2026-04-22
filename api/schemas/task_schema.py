"""Pydantic schemas for Task endpoints."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TaskCreate(BaseModel):
    task: str = Field(..., min_length=1, max_length=2000)
    priority: str = Field(default="medium")
    context: Optional[dict] = None


class TaskResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[str] = None
    trace: list = []
    duration_seconds: float = 0
    tools_used: list[str] = []
    iterations: int = 0
    error: Optional[str] = None

    class Config:
        from_attributes = True
