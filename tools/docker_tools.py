"""
DevOps Agent — Docker Tools
"""

import json
from tools.base import BaseTool
from config.constants import ToolCategory, RiskLevel, SIMULATION_RESPONSES


class BuildImage(BaseTool):
    name = "build_image"
    description = "Build a Docker image from a Dockerfile"
    category = ToolCategory.INFRASTRUCTURE
    risk_level = RiskLevel.MEDIUM
    parameters_schema = '{"path": "string", "tag": "string", "dockerfile": "string (optional)"}'

    def execute(self, **kwargs):
        if self.simulation_mode:
            tag = kwargs.get("tag", "app:latest")
            return json.dumps({"status": "built", "image": tag, "size": "145MB", "layers": 12, "build_time": "34s"})
        import docker
        client = docker.from_env()
        image, logs = client.images.build(path=kwargs.get("path", "."), tag=kwargs.get("tag", "app:latest"))
        return json.dumps({"image": image.tags[0], "id": image.short_id})


class ListContainers(BaseTool):
    name = "list_containers"
    description = "List Docker containers with status and resource usage"
    category = ToolCategory.INFRASTRUCTURE
    risk_level = RiskLevel.SAFE
    parameters_schema = '{"all": "boolean (optional, include stopped)"}'

    def execute(self, **kwargs):
        if self.simulation_mode:
            return json.dumps({"containers": SIMULATION_RESPONSES["docker"]["containers"], "total": 4})
        import docker
        client = docker.from_env()
        containers = client.containers.list(all=kwargs.get("all", False))
        return json.dumps({"containers": [{"name": c.name, "status": c.status, "image": c.image.tags[0] if c.image.tags else "unknown"} for c in containers]})


class ContainerLogs(BaseTool):
    name = "container_logs"
    description = "Fetch logs from a Docker container"
    category = ToolCategory.INFRASTRUCTURE
    risk_level = RiskLevel.SAFE
    parameters_schema = '{"container": "string", "tail": "integer (optional, default 50)"}'

    def execute(self, **kwargs):
        if self.simulation_mode:
            name = kwargs.get("container", "api-server")
            return json.dumps({
                "container": name, "lines": 50,
                "logs": f"[INFO] {name} started on port 8000\n[INFO] Connected to database\n[INFO] Health check: OK\n[WARN] High memory usage detected (78%)\n[INFO] Request processed in 245ms",
            })
        import docker
        client = docker.from_env()
        container = client.containers.get(kwargs["container"])
        logs = container.logs(tail=kwargs.get("tail", 50)).decode("utf-8")
        return json.dumps({"container": kwargs["container"], "logs": logs})


class RestartContainer(BaseTool):
    name = "restart_container"
    description = "Restart a Docker container"
    category = ToolCategory.INFRASTRUCTURE
    risk_level = RiskLevel.MEDIUM
    parameters_schema = '{"container": "string", "timeout": "integer (optional)"}'

    def execute(self, **kwargs):
        if self.simulation_mode:
            name = kwargs.get("container", "api-server")
            return json.dumps({"status": "restarted", "container": name, "downtime": "2.3s"})
        import docker
        client = docker.from_env()
        container = client.containers.get(kwargs["container"])
        container.restart(timeout=kwargs.get("timeout", 10))
        return json.dumps({"status": "restarted", "container": kwargs["container"]})


class PruneImages(BaseTool):
    name = "prune_images"
    description = "Remove unused Docker images to free disk space"
    category = ToolCategory.INFRASTRUCTURE
    risk_level = RiskLevel.MEDIUM
    parameters_schema = '{"all": "boolean (optional, remove all unused)"}'

    def execute(self, **kwargs):
        if self.simulation_mode:
            return json.dumps({"status": "pruned", "images_removed": 7, "space_reclaimed": "2.3GB"})
        import docker
        client = docker.from_env()
        result = client.images.prune(filters={"dangling": not kwargs.get("all", False)})
        reclaimed = result.get("SpaceReclaimed", 0) / (1024**3)
        return json.dumps({"images_removed": len(result.get("ImagesDeleted", [])), "space_reclaimed": f"{reclaimed:.1f}GB"})
