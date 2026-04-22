"""
DevOps Agent — Terraform Tools
"""

import json
from tools.base import BaseTool
from config.constants import ToolCategory, RiskLevel


class TerraformInit(BaseTool):
    name = "terraform_init"
    description = "Initialize a Terraform workspace"
    category = ToolCategory.INFRASTRUCTURE
    risk_level = RiskLevel.LOW
    parameters_schema = '{"workspace": "string (optional)"}'

    def execute(self, **kwargs):
        if self.simulation_mode:
            return json.dumps({"status": "initialized", "workspace": kwargs.get("workspace", "default"), "providers": ["aws v5.40.0", "kubernetes v2.27.0"]})
        import subprocess
        result = subprocess.run(["terraform", "init"], capture_output=True, text=True, cwd=kwargs.get("path", "."))
        return json.dumps({"stdout": result.stdout, "returncode": result.returncode})


class TerraformPlan(BaseTool):
    name = "terraform_plan"
    description = "Generate a Terraform execution plan showing proposed changes"
    category = ToolCategory.INFRASTRUCTURE
    risk_level = RiskLevel.SAFE
    parameters_schema = '{"workspace": "string (optional)"}'

    def execute(self, **kwargs):
        if self.simulation_mode:
            return json.dumps({
                "status": "planned", "changes": {"add": 3, "change": 1, "destroy": 0},
                "resources": [
                    {"action": "create", "resource": "aws_instance.web_server"},
                    {"action": "create", "resource": "aws_security_group.web_sg"},
                    {"action": "create", "resource": "aws_lb.web_lb"},
                    {"action": "update", "resource": "aws_route53_record.web_dns"},
                ],
            })
        import subprocess
        result = subprocess.run(["terraform", "plan", "-json"], capture_output=True, text=True)
        return result.stdout


class TerraformApply(BaseTool):
    name = "terraform_apply"
    description = "Apply Terraform changes to infrastructure (REQUIRES APPROVAL)"
    category = ToolCategory.INFRASTRUCTURE
    risk_level = RiskLevel.CRITICAL
    parameters_schema = '{"auto_approve": "boolean (optional, default false)"}'

    def execute(self, **kwargs):
        if self.simulation_mode:
            return json.dumps({"status": "applied", "resources_created": 3, "resources_updated": 1, "resources_destroyed": 0, "duration": "2m 34s"})
        import subprocess
        cmd = ["terraform", "apply"]
        if kwargs.get("auto_approve"):
            cmd.append("-auto-approve")
        result = subprocess.run(cmd, capture_output=True, text=True)
        return json.dumps({"stdout": result.stdout, "returncode": result.returncode})


class TerraformDestroy(BaseTool):
    name = "terraform_destroy"
    description = "Destroy all Terraform-managed infrastructure (DANGEROUS)"
    category = ToolCategory.INFRASTRUCTURE
    risk_level = RiskLevel.CRITICAL
    parameters_schema = '{"confirm": "boolean (must be true)"}'

    def execute(self, **kwargs):
        if not kwargs.get("confirm"):
            return json.dumps({"status": "blocked", "reason": "Must pass confirm=true to destroy infrastructure"})
        if self.simulation_mode:
            return json.dumps({"status": "destroyed", "resources_destroyed": 7, "duration": "3m 12s"})
        import subprocess
        result = subprocess.run(["terraform", "destroy", "-auto-approve"], capture_output=True, text=True)
        return json.dumps({"stdout": result.stdout, "returncode": result.returncode})


class GetTerraformState(BaseTool):
    name = "get_terraform_state"
    description = "Read the current Terraform state and list managed resources"
    category = ToolCategory.INFRASTRUCTURE
    risk_level = RiskLevel.SAFE
    parameters_schema = '{"workspace": "string (optional)"}'

    def execute(self, **kwargs):
        if self.simulation_mode:
            return json.dumps({
                "workspace": kwargs.get("workspace", "default"),
                "resources": [
                    {"type": "aws_vpc", "name": "main", "id": "vpc-0abc123"},
                    {"type": "aws_subnet", "name": "public_a", "id": "subnet-0def456"},
                    {"type": "aws_eks_cluster", "name": "production", "id": "eks-prod-001"},
                    {"type": "aws_rds_instance", "name": "primary", "id": "rds-prod-db"},
                ],
                "total_resources": 4,
            })
        import subprocess
        result = subprocess.run(["terraform", "state", "list"], capture_output=True, text=True)
        return json.dumps({"resources": result.stdout.strip().split("\n")})
