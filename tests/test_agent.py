import pytest
from agent.core import DevOpsAgent
from agent.react_engine import ReActEngine
from agent.planner import TaskPlanner
from config.constants import TaskPriority

def test_agent_initialization():
    agent = DevOpsAgent(simulation_mode=True)
    assert agent.engine is not None
    assert agent.planner is not None
    assert agent.memory is not None

def test_planner_decomposition():
    planner = TaskPlanner()
    
    # Test parallelizable task
    steps = planner.decompose("Check pod health and analyze logs")
    assert len(steps) > 0
    assert any("pod" in s.lower() for s in steps)
    
    # Test sequential task
    steps = planner.decompose("Deploy the new version then run tests")
    assert len(steps) == 2

def test_agent_run_simulation():
    agent = DevOpsAgent(simulation_mode=True)
    result = agent.run("List running docker containers", priority=TaskPriority.LOW)
    
    assert result["status"] == "success"
    assert "tools_used" in result
    assert "result" in result
    assert result["iterations"] >= 1
