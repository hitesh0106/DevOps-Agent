"""
DevOps Agent — Tool Registry
================================
Central registry that auto-discovers and manages all agent tools.
"""

from typing import Optional
from config.logging_config import get_logger
from config.constants import ToolCategory

from tools.base import BaseTool
from tools.github_tools import ListRepos, GetPRDetails, CreatePullRequest, GetCIStatus, GetFailingTests, PostComment, MergePR
from tools.docker_tools import BuildImage, ListContainers, ContainerLogs, RestartContainer, PruneImages
from tools.kubernetes_tools import GetPods, GetPodLogs, ScaleDeployment, RollbackDeployment, GetClusterHealth, ApplyManifest
from tools.terraform_tools import TerraformInit, TerraformPlan, TerraformApply, TerraformDestroy, GetTerraformState
from tools.shell_tools import SafeExecute
from tools.monitoring_tools import QueryPrometheus, GetAlerts, GetGrafanaDashboard, CheckServiceHealth
from tools.notification_tools import SendSlackMessage, SendEmail, CreatePagerDutyIncident
from tools.security_tools import ScanDockerImage, ScanDependencies, CheckSecrets, AuditPermissions
from tools.cost_tools import GetCloudCosts, FindIdleResources, RecommendSavings

logger = get_logger(__name__)


# All tool classes
ALL_TOOL_CLASSES = [
    # GitHub
    ListRepos, GetPRDetails, CreatePullRequest, GetCIStatus,
    GetFailingTests, PostComment, MergePR,
    # Docker
    BuildImage, ListContainers, ContainerLogs, RestartContainer, PruneImages,
    # Kubernetes
    GetPods, GetPodLogs, ScaleDeployment, RollbackDeployment,
    GetClusterHealth, ApplyManifest,
    # Terraform
    TerraformInit, TerraformPlan, TerraformApply, TerraformDestroy, GetTerraformState,
    # Shell
    SafeExecute,
    # Monitoring
    QueryPrometheus, GetAlerts, GetGrafanaDashboard, CheckServiceHealth,
    # Notifications
    SendSlackMessage, SendEmail, CreatePagerDutyIncident,
    # Security
    ScanDockerImage, ScanDependencies, CheckSecrets, AuditPermissions,
    # Cost
    GetCloudCosts, FindIdleResources, RecommendSavings,
]


class ToolRegistry:
    """
    Central tool registry — instantiates and manages all agent tools.
    """

    def __init__(self, simulation_mode: bool = True):
        self.simulation_mode = simulation_mode
        self._tools: dict[str, BaseTool] = {}
        self._register_all()

    def _register_all(self):
        """Instantiate and register all tool classes."""
        for tool_cls in ALL_TOOL_CLASSES:
            try:
                tool = tool_cls(simulation_mode=self.simulation_mode)
                self._tools[tool.name] = tool
            except Exception as e:
                logger.warning(f"Failed to register tool {tool_cls.__name__}: {e}")

        logger.info("Tool registry initialized", tools_count=len(self._tools))

    def get_all_tools(self) -> list[BaseTool]:
        """Return all registered tools."""
        return list(self._tools.values())

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(name)

    def get_by_category(self, category: ToolCategory) -> list[BaseTool]:
        """Get all tools in a category."""
        return [t for t in self._tools.values() if t.category == category]

    def list_tools(self) -> list[dict]:
        """List all tools with metadata."""
        return [
            {
                "name": t.name,
                "description": t.description,
                "category": t.category.value,
                "risk_level": t.risk_level.value,
            }
            for t in self._tools.values()
        ]
