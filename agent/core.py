
import sys
import time
import uuid
from datetime import datetime, timezone
from typing import Optional

from config.settings import settings
from config.logging_config import get_logger, setup_logging
from config.constants import AgentState, TaskStatus, TaskPriority

from agent.react_engine import ReActEngine
from agent.planner import TaskPlanner
from agent.memory.short_term import ShortTermMemory
from agent.memory.long_term import LongTermMemory
from agent.memory.episodic import EpisodicMemory

from tools.registry import ToolRegistry
from safety.guardrails import SafetyGuardrails

logger = get_logger(__name__)


class DevOpsAgent:
    """
    🧠 DevOps Agent — AI-Powered Infrastructure Automation
    
    The central orchestrator that:
    1. Receives tasks (from API, webhooks, or CLI)
    2. Plans execution strategy
    3. Runs the ReAct (Reason + Act) loop
    4. Manages tools, memory, and safety
    5. Returns results with full execution trace
    
    Architecture:
        Task Input → Planner → ReAct Engine → Tools → Safety → Output
                                    ↑                      |
                                    └──── Memory ──────────┘
    """

    def __init__(self, verbose: bool = False):
        """
        Initialize the DevOps Agent with all subsystems.
        
        Args:
            verbose: If True, print detailed ReAct execution trace
        """
        self.agent_id = str(uuid.uuid4())[:8]
        self.verbose = verbose
        self.state = AgentState.IDLE
        self.created_at = datetime.now(timezone.utc)
        
        # Initialize subsystems
        logger.info("Initializing DevOps Agent", agent_id=self.agent_id)
        
        # 1. Tool Registry — All available tools
        self.tool_registry = ToolRegistry(simulation_mode=settings.simulation_mode)
        
        # 2. Safety Guardrails — Command validation
        self.safety = SafetyGuardrails()
        
        # 3. Memory Systems
        self.short_term = ShortTermMemory(max_entries=50)
        self.long_term = LongTermMemory(
            collection_name=settings.agent.agent_memory_collection,
            persist_dir=settings.agent.chroma_persist_dir,
        )
        self.episodic = EpisodicMemory()
        
        # 4. Task Planner — Decomposes complex tasks
        self.planner = TaskPlanner()
        
        # 5. ReAct Engine — The reasoning loop
        self.react_engine = ReActEngine(
            tools=self.tool_registry.get_all_tools(),
            safety=self.safety,
            short_term_memory=self.short_term,
            long_term_memory=self.long_term,
            max_iterations=settings.agent.agent_max_iterations,
            verbose=self.verbose,
        )
        
        logger.info(
            "DevOps Agent initialized",
            agent_id=self.agent_id,
            tools_count=len(self.tool_registry.get_all_tools()),
            simulation_mode=settings.simulation_mode,
        )

    def run(self, task: str, priority: TaskPriority = TaskPriority.MEDIUM,
            context: Optional[dict] = None) -> dict:
        """
        Execute a DevOps task using the ReAct reasoning loop.
        
        Args:
            task: Natural language task description
            priority: Task priority level
            context: Additional context (e.g., webhook payload, alert data)
            
        Returns:
            dict with keys:
                - task_id: Unique task identifier
                - status: "completed" or "failed"
                - result: Final answer from the agent
                - trace: List of ReAct steps (thought, action, observation)
                - duration_seconds: Total execution time
                - tools_used: List of tools invoked
                - error: Error message if failed
                
        Example:
            agent = DevOpsAgent()
            result = agent.run("Check pod health in production namespace")
            print(result["result"])
        """
        task_id = str(uuid.uuid4())[:12]
        start_time = time.time()
        
        logger.info(
            "Task received",
            task_id=task_id,
            task=task[:100],
            priority=priority.value,
        )
        
        self.state = AgentState.THINKING
        
        try:
            # Step 1: Search memory for similar past tasks
            similar_incidents = self.long_term.search_similar(task, k=3)
            if similar_incidents:
                logger.info(
                    "Found similar past incidents",
                    task_id=task_id,
                    count=len(similar_incidents),
                )
            
            # Step 2: Plan the task (decompose if complex)
            plan = self.planner.plan(task, context=context)
            logger.info(
                "Task plan created",
                task_id=task_id,
                steps=len(plan.steps) if plan.steps else 1,
            )
            
            # Step 3: Execute via ReAct Engine
            react_result = self.react_engine.execute(
                task=task,
                context={
                    "priority": priority.value,
                    "similar_incidents": similar_incidents,
                    "plan": plan.to_dict(),
                    **(context or {}),
                }
            )
            
            # Step 4: Store resolution in long-term memory
            self.long_term.store_resolution(
                task=task,
                resolution=react_result["final_answer"],
                tools_used=react_result["tools_used"],
                success=react_result["success"],
            )
            
            # Step 5: Store in episodic memory
            self.episodic.store_episode(
                task_id=task_id,
                task=task,
                result=react_result["final_answer"],
                steps=react_result["trace"],
                success=react_result["success"],
            )
            
            duration = time.time() - start_time
            self.state = AgentState.COMPLETED
            
            result = {
                "task_id": task_id,
                "status": TaskStatus.COMPLETED.value if react_result["success"] else TaskStatus.FAILED.value,
                "result": react_result["final_answer"],
                "trace": react_result["trace"],
                "duration_seconds": round(duration, 2),
                "tools_used": react_result["tools_used"],
                "iterations": react_result["iterations"],
                "error": None,
            }
            
            logger.info(
                "Task completed",
                task_id=task_id,
                status=result["status"],
                duration=result["duration_seconds"],
                iterations=result["iterations"],
                tools_used=result["tools_used"],
            )
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            self.state = AgentState.FAILED
            
            error_result = {
                "task_id": task_id,
                "status": TaskStatus.FAILED.value,
                "result": None,
                "trace": [],
                "duration_seconds": round(duration, 2),
                "tools_used": [],
                "iterations": 0,
                "error": str(e),
            }
            
            logger.error(
                "Task failed",
                task_id=task_id,
                error=str(e),
                duration=round(duration, 2),
            )
            
            return error_result

    def get_status(self) -> dict:
        """Get the current agent status."""
        return {
            "agent_id": self.agent_id,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "tools_available": len(self.tool_registry.get_all_tools()),
            "memory_entries": self.short_term.size(),
            "simulation_mode": settings.simulation_mode,
        }

    def get_available_tools(self) -> list[dict]:
        """List all available tools with descriptions."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "category": tool.category,
                "risk_level": tool.risk_level,
            }
            for tool in self.tool_registry.get_all_tools()
        ]


def main():
    """CLI entry point for running the agent."""
    setup_logging(log_level=settings.log_level)
    
    # Parse CLI arguments
    if len(sys.argv) < 2:
        print("\n🤖 DevOps Agent — AI-Powered Infrastructure Automation")
        print("=" * 55)
        print("\nUsage:")
        print('  python -m agent.core "Your DevOps task here"')
        print('  python -m agent.core "Check pod health" --verbose')
        print("\nExamples:")
        print('  python -m agent.core "List all running Docker containers"')
        print('  python -m agent.core "Check the health of Kubernetes pods"')
        print('  python -m agent.core "Analyze CI/CD pipeline status"')
        print('  python -m agent.core "Scan for security vulnerabilities"')
        print('  python -m agent.core "Show cloud cost analysis"')
        sys.exit(0)
    
    task = sys.argv[1]
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    print(f"\n{'='*60}")
    print(f"🤖 DevOps Agent")
    print(f"{'='*60}")
    print(f"📋 Task: {task}")
    print(f"🔧 Mode: {'Simulation' if settings.simulation_mode else 'Production'}")
    print(f"{'='*60}\n")
    
    # Create and run agent
    agent = DevOpsAgent(verbose=verbose)
    result = agent.run(task)
    
    # Display results
    print(f"\n{'='*60}")
    print(f"📊 RESULT")
    print(f"{'='*60}")
    print(f"Status: {'✅ Completed' if result['status'] == 'completed' else '❌ Failed'}")
    print(f"Duration: {result['duration_seconds']}s")
    print(f"Iterations: {result['iterations']}")
    print(f"Tools Used: {', '.join(result['tools_used']) or 'None'}")
    print(f"\n{'─'*60}")
    print(f"💡 Answer:\n{result['result']}")
    
    if result.get("error"):
        print(f"\n❌ Error: {result['error']}")
    
    if verbose and result.get("trace"):
        print(f"\n{'='*60}")
        print(f"🔍 EXECUTION TRACE")
        print(f"{'='*60}")
        for i, step in enumerate(result["trace"], 1):
            print(f"\n── Step {i} ──")
            print(f"💭 Thought: {step.get('thought', 'N/A')}")
            print(f"🔧 Action: {step.get('action', 'N/A')}")
            print(f"📝 Input: {step.get('action_input', 'N/A')}")
            print(f"👁️  Observation: {step.get('observation', 'N/A')[:200]}")
    
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
