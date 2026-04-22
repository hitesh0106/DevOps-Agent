"""
DevOps Agent — Global Constants & Enums
========================================
Defines all constant values and enumerations used throughout the project.
"""

from enum import Enum


# ── Agent States ──────────────────────────────────
class AgentState(str, Enum):
    """Possible states of the DevOps Agent."""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    OBSERVING = "observing"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


# ── Task Priority ────────────────────────────────
class TaskPriority(str, Enum):
    """Task priority levels."""
    CRITICAL = "critical"      # P1 — Immediate response
    HIGH = "high"              # P2 — Within 15 minutes
    MEDIUM = "medium"          # P3 — Within 1 hour
    LOW = "low"                # P4 — Best effort


# ── Task Status ──────────────────────────────────
class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    WAITING_APPROVAL = "waiting_approval"


# ── Pipeline Status ──────────────────────────────
class PipelineStatus(str, Enum):
    """CI/CD Pipeline status."""
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ── Incident Severity ───────────────────────────
class IncidentSeverity(str, Enum):
    """Incident severity levels."""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


# ── Tool Categories ─────────────────────────────
class ToolCategory(str, Enum):
    """Categories for agent tools."""
    CICD = "ci_cd"
    INFRASTRUCTURE = "infrastructure"
    MONITORING = "monitoring"
    SECURITY = "security"
    NOTIFICATION = "notification"
    SHELL = "shell"
    COST = "cost"


# ── Safety Risk Levels ──────────────────────────
class RiskLevel(str, Enum):
    """Risk level for agent actions."""
    SAFE = "safe"                  # No approval needed
    LOW = "low"                    # Logged, no approval
    MEDIUM = "medium"              # Logged, optional approval
    HIGH = "high"                  # Requires human approval
    CRITICAL = "critical"          # Blocked by default


# ── Webhook Event Types ─────────────────────────
class WebhookEvent(str, Enum):
    """Supported webhook event types."""
    GITHUB_PUSH = "github.push"
    GITHUB_PR = "github.pull_request"
    GITHUB_CI_FAILURE = "github.check_run.failure"
    ALERTMANAGER_ALERT = "alertmanager.alert"
    CUSTOM_EVENT = "custom.event"


# ── Color Codes for Terminal Output ─────────────
class Colors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    DIM = "\033[2m"


# ── Agent Limits ────────────────────────────────
MAX_REACT_ITERATIONS = 15
MAX_TOOL_OUTPUT_LENGTH = 5000
MAX_MEMORY_RESULTS = 5
TASK_TIMEOUT_SECONDS = 300
APPROVAL_TIMEOUT_SECONDS = 600

# ── Dangerous Command Patterns ──────────────────
BLOCKED_COMMANDS = [
    "rm -rf /",
    "rm -rf /*",
    "mkfs.",
    "dd if=/dev/zero",
    ":(){:|:&};:",
    "chmod -R 777 /",
    "shutdown",
    "reboot",
    "halt",
    "poweroff",
]

APPROVAL_REQUIRED_PATTERNS = [
    "terraform destroy",
    "terraform apply",
    "kubectl delete namespace",
    "kubectl delete deployment",
    "DROP TABLE",
    "DROP DATABASE",
    "TRUNCATE",
    "--force",
    "--grace-period=0",
    "scale --replicas=0",
]

# ── Simulation Responses ────────────────────────
SIMULATION_RESPONSES = {
    "github": {
        "repos": ["frontend-app", "backend-api", "infra-config", "ml-service"],
        "status": "All CI checks passing ✅",
    },
    "docker": {
        "containers": [
            {"name": "api-server", "status": "running", "cpu": "12%", "memory": "256MB"},
            {"name": "postgres-db", "status": "running", "cpu": "5%", "memory": "512MB"},
            {"name": "redis-cache", "status": "running", "cpu": "2%", "memory": "64MB"},
            {"name": "nginx-proxy", "status": "running", "cpu": "1%", "memory": "32MB"},
        ],
    },
    "kubernetes": {
        "pods": [
            {"name": "api-server-7d8f9c-x2k4t", "status": "Running", "restarts": 0, "age": "3d"},
            {"name": "worker-5c6d7e-m9n2p", "status": "Running", "restarts": 0, "age": "3d"},
            {"name": "scheduler-4b5c6d-q8r1s", "status": "Running", "restarts": 1, "age": "5d"},
        ],
        "cluster_health": "Healthy — 3/3 nodes ready, 12 pods running",
    },
    "prometheus": {
        "cpu_usage": "34.2%",
        "memory_usage": "67.8%",
        "error_rate": "0.12%",
        "request_latency_p99": "245ms",
    },
}
