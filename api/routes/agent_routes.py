"""
DevOps Agent — Agent Task Routes
"""

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional
from agent.core import DevOpsAgent
from config.constants import TaskPriority

router = APIRouter()

# Shared agent instance
_agent: Optional[DevOpsAgent] = None


def get_agent() -> DevOpsAgent:
    global _agent
    if _agent is None:
        _agent = DevOpsAgent()
    return _agent


class TaskRequest(BaseModel):
    task: str = Field(..., description="Natural language task description")
    priority: str = Field(default="medium", description="Task priority")
    context: Optional[dict] = Field(default=None, description="Additional context")


class TaskResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[str] = None
    trace: list = []
    duration_seconds: float = 0
    tools_used: list = []
    iterations: int = 0
    error: Optional[str] = None


@router.post("/task", response_model=TaskResponse)
async def submit_task(request: TaskRequest):
    """Submit a task for the agent to execute."""
    agent = get_agent()
    priority = TaskPriority(request.priority) if request.priority in [p.value for p in TaskPriority] else TaskPriority.MEDIUM
    result = agent.run(task=request.task, priority=priority, context=request.context)
    return TaskResponse(**result)


@router.get("/status")
async def agent_status():
    """Get agent status and capabilities."""
    agent = get_agent()
    return agent.get_status()


@router.get("/tools")
async def list_tools():
    """List all available agent tools."""
    agent = get_agent()
    return {"tools": agent.get_available_tools()}
