"""
DevOps Agent — Task Planner
==============================
Breaks down complex DevOps tasks into structured sub-tasks
with dependency ordering and execution strategies.
"""

from dataclasses import dataclass, field
from typing import Optional
from config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class PlanStep:
    """A single step in a task plan."""
    id: int
    description: str
    tool_hint: str = ""
    depends_on: list[int] = field(default_factory=list)
    parallel: bool = False
    estimated_duration: str = "unknown"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "description": self.description,
            "tool_hint": self.tool_hint,
            "depends_on": self.depends_on,
            "parallel": self.parallel,
            "estimated_duration": self.estimated_duration,
        }


@dataclass
class TaskPlan:
    """A structured plan for executing a DevOps task."""
    task: str
    strategy: str = "sequential"  # sequential, parallel, mixed
    steps: list[PlanStep] = field(default_factory=list)
    estimated_total_duration: str = "unknown"

    def to_dict(self) -> dict:
        return {
            "task": self.task,
            "strategy": self.strategy,
            "steps": [s.to_dict() for s in self.steps],
            "estimated_total_duration": self.estimated_total_duration,
        }


# ── Keyword-to-plan mapping ──────────────────────────
TASK_PATTERNS = {
    "health": {
        "strategy": "sequential",
        "steps": [
            {"description": "Check cluster node status", "tool_hint": "get_cluster_health"},
            {"description": "List pods and their states", "tool_hint": "get_pods"},
            {"description": "Check resource utilization", "tool_hint": "query_prometheus"},
            {"description": "Compile health report", "tool_hint": ""},
        ],
    },
    "deploy": {
        "strategy": "sequential",
        "steps": [
            {"description": "Validate deployment manifest", "tool_hint": ""},
            {"description": "Run pre-deploy security scan", "tool_hint": "scan_docker_image"},
            {"description": "Apply Kubernetes manifest", "tool_hint": "apply_manifest"},
            {"description": "Verify rollout status", "tool_hint": "get_pods"},
            {"description": "Run post-deploy health check", "tool_hint": "check_service_health"},
        ],
    },
    "ci": {
        "strategy": "sequential",
        "steps": [
            {"description": "Check CI pipeline status", "tool_hint": "get_ci_status"},
            {"description": "Retrieve failing test logs", "tool_hint": "get_failing_tests"},
            {"description": "Analyze root cause", "tool_hint": ""},
            {"description": "Suggest fix and create PR", "tool_hint": "create_pull_request"},
        ],
    },
    "security": {
        "strategy": "parallel",
        "steps": [
            {"description": "Scan Docker images for CVEs", "tool_hint": "scan_docker_image"},
            {"description": "Scan dependencies for vulnerabilities", "tool_hint": "scan_dependencies"},
            {"description": "Check for leaked secrets", "tool_hint": "check_secrets"},
            {"description": "Audit RBAC permissions", "tool_hint": "audit_permissions"},
            {"description": "Compile security report", "tool_hint": ""},
        ],
    },
    "cost": {
        "strategy": "sequential",
        "steps": [
            {"description": "Get current cloud spending", "tool_hint": "get_cloud_costs"},
            {"description": "Find idle resources", "tool_hint": "find_idle_resources"},
            {"description": "Generate savings recommendations", "tool_hint": "recommend_savings"},
        ],
    },
    "incident": {
        "strategy": "sequential",
        "steps": [
            {"description": "Gather alert details", "tool_hint": "get_alerts"},
            {"description": "Check affected service health", "tool_hint": "check_service_health"},
            {"description": "Retrieve recent logs", "tool_hint": "get_pod_logs"},
            {"description": "Search for similar past incidents", "tool_hint": ""},
            {"description": "Apply resolution and verify", "tool_hint": ""},
            {"description": "Send notification", "tool_hint": "send_slack_message"},
        ],
    },
    "terraform": {
        "strategy": "sequential",
        "steps": [
            {"description": "Initialize Terraform workspace", "tool_hint": "terraform_init"},
            {"description": "Generate execution plan", "tool_hint": "terraform_plan"},
            {"description": "Review planned changes", "tool_hint": ""},
            {"description": "Apply infrastructure changes", "tool_hint": "terraform_apply"},
            {"description": "Verify deployed resources", "tool_hint": "get_terraform_state"},
        ],
    },
}


class TaskPlanner:
    """
    Decomposes complex DevOps tasks into structured plans.

    Uses keyword matching to create execution plans.
    In production, the LLM would generate these plans dynamically.
    """

    def plan(self, task: str, context: Optional[dict] = None) -> TaskPlan:
        """
        Create an execution plan for a task.

        Args:
            task: Natural language task description
            context: Additional context from webhooks, alerts, etc.

        Returns:
            TaskPlan with ordered steps
        """
        task_lower = task.lower()

        # Find matching pattern
        matched_pattern = None
        for keyword, pattern in TASK_PATTERNS.items():
            if keyword in task_lower:
                matched_pattern = pattern
                logger.info("Task pattern matched", keyword=keyword, task=task[:60])
                break

        if not matched_pattern:
            # Default single-step plan
            logger.info("No pattern matched, using generic plan", task=task[:60])
            return TaskPlan(
                task=task,
                strategy="sequential",
                steps=[
                    PlanStep(id=1, description=f"Execute: {task}", tool_hint=""),
                ],
            )

        # Build plan from pattern
        steps = []
        for i, step_def in enumerate(matched_pattern["steps"], 1):
            steps.append(PlanStep(
                id=i,
                description=step_def["description"],
                tool_hint=step_def.get("tool_hint", ""),
                depends_on=[i - 1] if i > 1 and matched_pattern["strategy"] == "sequential" else [],
            ))

        plan = TaskPlan(
            task=task,
            strategy=matched_pattern["strategy"],
            steps=steps,
        )

        logger.info(
            "Task plan created",
            task=task[:60],
            strategy=plan.strategy,
            steps_count=len(plan.steps),
        )

        return plan
