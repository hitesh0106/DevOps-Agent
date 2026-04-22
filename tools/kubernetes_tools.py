"""
DevOps Agent — Kubernetes Tools
"""

import json
from tools.base import BaseTool
from config.constants import ToolCategory, RiskLevel, SIMULATION_RESPONSES


class GetPods(BaseTool):
    name = "get_pods"
    description = "List Kubernetes pods with status, restarts, and age"
    category = ToolCategory.INFRASTRUCTURE
    risk_level = RiskLevel.SAFE
    parameters_schema = '{"namespace": "string (optional, default: default)"}'

    def execute(self, **kwargs):
        if self.simulation_mode:
            return json.dumps({"namespace": kwargs.get("namespace", "default"), "pods": SIMULATION_RESPONSES["kubernetes"]["pods"]})
        from kubernetes import client, config
        config.load_kube_config()
        v1 = client.CoreV1Api()
        ns = kwargs.get("namespace", "default")
        pods = v1.list_namespaced_pod(ns)
        return json.dumps({"pods": [{"name": p.metadata.name, "status": p.status.phase, "restarts": sum(cs.restart_count for cs in (p.status.container_statuses or []))} for p in pods.items]})


class GetPodLogs(BaseTool):
    name = "get_pod_logs"
    description = "Fetch logs from a Kubernetes pod"
    category = ToolCategory.INFRASTRUCTURE
    risk_level = RiskLevel.SAFE
    parameters_schema = '{"pod": "string", "namespace": "string (optional)", "tail_lines": "integer (optional)"}'

    def execute(self, **kwargs):
        if self.simulation_mode:
            pod = kwargs.get("pod", "api-server-7d8f9c-x2k4t")
            return json.dumps({"pod": pod, "logs": f"[INFO] Pod {pod} running\n[INFO] Health check passed\n[INFO] Serving requests on :8080"})
        from kubernetes import client, config
        config.load_kube_config()
        v1 = client.CoreV1Api()
        logs = v1.read_namespaced_pod_log(kwargs["pod"], kwargs.get("namespace", "default"), tail_lines=kwargs.get("tail_lines", 100))
        return json.dumps({"pod": kwargs["pod"], "logs": logs})


class ScaleDeployment(BaseTool):
    name = "scale_deployment"
    description = "Scale a Kubernetes deployment up or down"
    category = ToolCategory.INFRASTRUCTURE
    risk_level = RiskLevel.HIGH
    parameters_schema = '{"deployment": "string", "replicas": "integer", "namespace": "string (optional)"}'

    def execute(self, **kwargs):
        if self.simulation_mode:
            return json.dumps({"deployment": kwargs.get("deployment", "api-server"), "replicas": kwargs.get("replicas", 3), "status": "scaled"})
        from kubernetes import client, config
        config.load_kube_config()
        apps = client.AppsV1Api()
        body = {"spec": {"replicas": kwargs["replicas"]}}
        apps.patch_namespaced_deployment_scale(kwargs["deployment"], kwargs.get("namespace", "default"), body)
        return json.dumps({"status": "scaled", "deployment": kwargs["deployment"], "replicas": kwargs["replicas"]})


class RollbackDeployment(BaseTool):
    name = "rollback_deployment"
    description = "Rollback a Kubernetes deployment to the previous version"
    category = ToolCategory.INFRASTRUCTURE
    risk_level = RiskLevel.HIGH
    parameters_schema = '{"deployment": "string", "namespace": "string (optional)", "revision": "integer (optional)"}'

    def execute(self, **kwargs):
        if self.simulation_mode:
            return json.dumps({"deployment": kwargs.get("deployment", "api-server"), "status": "rolled_back", "revision": kwargs.get("revision", "previous")})
        return json.dumps({"status": "rollback_initiated", "note": "Use kubectl rollout undo"})


class GetClusterHealth(BaseTool):
    name = "get_cluster_health"
    description = "Get overall Kubernetes cluster health status"
    category = ToolCategory.INFRASTRUCTURE
    risk_level = RiskLevel.SAFE
    parameters_schema = '{}'

    def execute(self, **kwargs):
        if self.simulation_mode:
            return json.dumps({
                "cluster_health": SIMULATION_RESPONSES["kubernetes"]["cluster_health"],
                "nodes": [
                    {"name": "node-1", "status": "Ready", "cpu": "45%", "memory": "62%"},
                    {"name": "node-2", "status": "Ready", "cpu": "32%", "memory": "58%"},
                    {"name": "node-3", "status": "Ready", "cpu": "28%", "memory": "71%"},
                ],
            })
        from kubernetes import client, config
        config.load_kube_config()
        v1 = client.CoreV1Api()
        nodes = v1.list_node()
        return json.dumps({"nodes": [{"name": n.metadata.name, "status": [c.type for c in n.status.conditions if c.status == "True"]} for n in nodes.items]})


class ApplyManifest(BaseTool):
    name = "apply_manifest"
    description = "Apply a Kubernetes YAML manifest"
    category = ToolCategory.INFRASTRUCTURE
    risk_level = RiskLevel.HIGH
    parameters_schema = '{"manifest_path": "string", "namespace": "string (optional)"}'

    def execute(self, **kwargs):
        if self.simulation_mode:
            return json.dumps({"status": "applied", "manifest": kwargs.get("manifest_path", "deployment.yaml"), "resources_created": 2})
        return json.dumps({"status": "apply_initiated", "note": "Use kubectl apply -f"})
