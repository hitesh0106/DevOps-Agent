import json
import pytest
from tools.registry import ToolRegistry
from tools.shell_tools import SafeExecute
from tools.kubernetes_tools import GetPods
from tools.docker_tools import ListContainers

def test_tool_registry():
    registry = ToolRegistry(simulation_mode=True)
    registry.discover_tools()
    
    assert len(registry.get_all_tools()) > 0
    assert registry.get_tool("safe_execute") is not None
    assert registry.get_tool("get_pods") is not None

def test_safe_execute_simulation():
    tool = SafeExecute(simulation_mode=True)
    
    # Test allowed command
    result = tool.execute(command="ls -la")
    data = json.loads(result)
    assert data["returncode"] == 0
    assert "simulated" in data
    
    # Test blocked command
    result = tool.execute(command="rm -rf /")
    data = json.loads(result)
    assert data["status"] == "BLOCKED"

def test_k8s_tools_simulation():
    tool = GetPods(simulation_mode=True)
    result = tool.execute(namespace="kube-system")
    data = json.loads(result)
    
    assert "pods" in data
    assert data["namespace"] == "kube-system"
    assert len(data["pods"]) > 0

def test_docker_tools_simulation():
    tool = ListContainers(simulation_mode=True)
    result = tool.execute()
    data = json.loads(result)
    
    assert "containers" in data
    assert data["total"] == 4
