"""
DevOps Agent — ReAct Engine
=============================
Implementation of the ReAct (Reasoning + Acting) loop.

The engine follows this cycle:
    1. THINK  — LLM analyzes the situation and decides what to do
    2. ACT    — Execute the chosen tool with parameters
    3. OBSERVE — Capture the tool's output
    4. REPEAT — Until the task is complete or max iterations reached

This is the core "brain" of the DevOps Agent.
"""

import json
import time
import re
from typing import Optional
from datetime import datetime, timezone

from config.logging_config import get_logger
from config.constants import AgentState, MAX_TOOL_OUTPUT_LENGTH
from config.settings import settings

logger = get_logger(__name__)

# ── ReAct Prompt Template ──────────────────────────────────
REACT_SYSTEM_PROMPT = """You are an expert DevOps Agent with access to tools for managing cloud infrastructure, CI/CD pipelines, Kubernetes clusters, Docker containers, and monitoring systems.

You operate using the ReAct (Reasoning + Acting) pattern. For each step:
1. Think about what you need to do
2. Choose a tool and provide its input
3. Observe the result
4. Repeat until the task is complete

AVAILABLE TOOLS:
{tools_description}

RESPONSE FORMAT (follow EXACTLY):
Thought: <your reasoning about what to do next>
Action: <tool_name>
Action Input: <parameters as JSON>

When you have the final answer:
Thought: I now have enough information to answer.
Final Answer: <your comprehensive answer>

RULES:
- Always start with a Thought
- Use tools to gather real data — never make assumptions
- If a tool fails, try an alternative approach
- Be concise but thorough in your final answer
- For destructive operations, always mention the safety implications
- Maximum {max_iterations} steps allowed

CONTEXT:
{context}

SIMILAR PAST INCIDENTS:
{similar_incidents}
"""

REACT_USER_PROMPT = """Task: {task}

Begin your analysis. Start with a Thought."""


class ReActStep:
    """Represents a single step in the ReAct loop."""
    
    def __init__(self, iteration: int):
        self.iteration = iteration
        self.thought: str = ""
        self.action: str = ""
        self.action_input: str = ""
        self.observation: str = ""
        self.timestamp = datetime.now(timezone.utc)
        self.duration_ms: float = 0
    
    def to_dict(self) -> dict:
        return {
            "iteration": self.iteration,
            "thought": self.thought,
            "action": self.action,
            "action_input": self.action_input,
            "observation": self.observation,
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": self.duration_ms,
        }


class ReActEngine:
    """
    The ReAct (Reason + Act) Engine.
    
    Implements the core reasoning loop where the LLM:
    1. Thinks about the current situation
    2. Decides which tool to use
    3. Observes the tool output
    4. Repeats until task completion
    """
    
    def __init__(
        self,
        tools: list,
        safety,
        short_term_memory,
        long_term_memory,
        max_iterations: int = 15,
        verbose: bool = False,
    ):
        self.tools = {tool.name: tool for tool in tools}
        self.safety = safety
        self.short_term = short_term_memory
        self.long_term = long_term_memory
        self.max_iterations = max_iterations
        self.verbose = verbose
        
        # Build tools description for the prompt
        self.tools_description = self._build_tools_description()
        
        # Initialize LLM
        self.llm = self._init_llm()
    
    def _init_llm(self):
        """Initialize the LLM based on configuration."""
        if settings.simulation_mode:
            return SimulatedLLM()
        
        provider = settings.llm.llm_provider
        
        if provider == "anthropic":
            try:
                from langchain_anthropic import ChatAnthropic
                return ChatAnthropic(
                    model=settings.llm.anthropic_model,
                    api_key=settings.llm.anthropic_api_key,
                    max_tokens=4096,
                    temperature=0.1,
                )
            except ImportError:
                logger.warning("langchain-anthropic not installed, falling back to simulation")
                return SimulatedLLM()
        elif provider == "openai":
            try:
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(
                    model=settings.llm.openai_model,
                    api_key=settings.llm.openai_api_key,
                    max_tokens=4096,
                    temperature=0.1,
                )
            except ImportError:
                logger.warning("langchain-openai not installed, falling back to simulation")
                return SimulatedLLM()
        else:
            return SimulatedLLM()
    
    def _build_tools_description(self) -> str:
        """Build a formatted description of all available tools."""
        descriptions = []
        for name, tool in self.tools.items():
            desc = f"- {name}: {tool.description}"
            if hasattr(tool, 'parameters_schema'):
                desc += f"\n  Parameters: {tool.parameters_schema}"
            descriptions.append(desc)
        return "\n".join(descriptions)
    
    def execute(self, task: str, context: Optional[dict] = None) -> dict:
        """
        Execute the ReAct loop for a given task.
        
        Args:
            task: Natural language task description
            context: Additional context (priority, similar incidents, plan)
            
        Returns:
            dict with final_answer, trace, tools_used, success, iterations
        """
        context = context or {}
        trace: list[dict] = []
        tools_used: list[str] = []
        final_answer = ""
        success = False
        
        # Format similar incidents
        similar = context.get("similar_incidents", [])
        similar_text = "None found" if not similar else "\n".join(
            f"- {inc.get('task', 'N/A')}: {inc.get('resolution', 'N/A')}" 
            for inc in similar
        )
        
        # Build conversation history
        conversation = []
        
        # System message
        system_message = REACT_SYSTEM_PROMPT.format(
            tools_description=self.tools_description,
            max_iterations=self.max_iterations,
            context=json.dumps(context.get("plan", {}), indent=2) if context.get("plan") else "No additional context",
            similar_incidents=similar_text,
        )
        
        # User message
        user_message = REACT_USER_PROMPT.format(task=task)
        
        conversation.append({"role": "system", "content": system_message})
        conversation.append({"role": "user", "content": user_message})
        
        logger.info("Starting ReAct loop", task=task[:80], max_iterations=self.max_iterations)
        
        for iteration in range(1, self.max_iterations + 1):
            step = ReActStep(iteration)
            step_start = time.time()
            
            if self.verbose:
                print(f"\n{'─'*50}")
                print(f"  Step {iteration}/{self.max_iterations}")
                print(f"{'─'*50}")
            
            # Get LLM response
            try:
                llm_response = self._call_llm(conversation)
            except Exception as e:
                logger.error("LLM call failed", error=str(e), iteration=iteration)
                step.thought = f"LLM Error: {str(e)}"
                step.observation = "Failed to get LLM response"
                trace.append(step.to_dict())
                break
            
            # Parse the response
            parsed = self._parse_response(llm_response)
            
            step.thought = parsed.get("thought", "")
            
            if self.verbose:
                print(f"  💭 Thought: {step.thought}")
            
            # Check if we have a final answer
            if parsed.get("final_answer"):
                final_answer = parsed["final_answer"]
                success = True
                step.action = "Final Answer"
                step.observation = final_answer
                step.duration_ms = (time.time() - step_start) * 1000
                trace.append(step.to_dict())
                
                if self.verbose:
                    print(f"  ✅ Final Answer: {final_answer[:200]}")
                
                logger.info("ReAct loop completed", iterations=iteration)
                break
            
            # Execute the action
            action_name = parsed.get("action", "")
            action_input = parsed.get("action_input", "{}")
            
            step.action = action_name
            step.action_input = action_input
            
            if self.verbose:
                print(f"  🔧 Action: {action_name}")
                print(f"  📥 Input: {action_input}")
            
            # Safety check
            safety_result = self.safety.check_action(action_name, action_input)
            if not safety_result["allowed"]:
                observation = f"⚠️ BLOCKED by safety guardrails: {safety_result['reason']}"
                step.observation = observation
                conversation.append({"role": "assistant", "content": llm_response})
                conversation.append({"role": "user", "content": f"Observation: {observation}\n\nChoose a safer alternative."})
                
                if self.verbose:
                    print(f"  🛡️ Blocked: {safety_result['reason']}")
                
                step.duration_ms = (time.time() - step_start) * 1000
                trace.append(step.to_dict())
                continue
            
            # Execute the tool
            observation = self._execute_tool(action_name, action_input)
            step.observation = observation[:MAX_TOOL_OUTPUT_LENGTH]
            
            if action_name and action_name not in tools_used:
                tools_used.append(action_name)
            
            if self.verbose:
                print(f"  👁️  Observation: {observation[:300]}")
            
            # Add to conversation
            conversation.append({"role": "assistant", "content": llm_response})
            conversation.append({"role": "user", "content": f"Observation: {observation}"})
            
            # Store in short-term memory
            self.short_term.add(
                role="step",
                content=f"Step {iteration}: {step.thought} → {action_name} → {observation[:200]}"
            )
            
            step.duration_ms = (time.time() - step_start) * 1000
            trace.append(step.to_dict())
        
        else:
            # Max iterations reached
            final_answer = f"Task exceeded maximum iterations ({self.max_iterations}). " \
                          f"Partial progress: {trace[-1]['observation'] if trace else 'None'}"
            logger.warning("Max iterations reached", max=self.max_iterations)
        
        return {
            "final_answer": final_answer,
            "trace": trace,
            "tools_used": tools_used,
            "success": success,
            "iterations": len(trace),
        }
    
    def _call_llm(self, conversation: list[dict]) -> str:
        """Call the LLM with conversation history."""
        if isinstance(self.llm, SimulatedLLM):
            return self.llm.invoke(conversation)
        
        # Convert to LangChain message format
        from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
        
        messages = []
        for msg in conversation:
            if msg["role"] == "system":
                messages.append(SystemMessage(content=msg["content"]))
            elif msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        response = self.llm.invoke(messages)
        return response.content
    
    def _parse_response(self, response: str) -> dict:
        """
        Parse LLM response to extract Thought, Action, Action Input, or Final Answer.
        
        Expected format:
            Thought: <reasoning>
            Action: <tool_name>
            Action Input: <json_params>
            
        Or:
            Thought: <reasoning>
            Final Answer: <answer>
        """
        result = {
            "thought": "",
            "action": "",
            "action_input": "",
            "final_answer": "",
        }
        
        # Extract Thought
        thought_match = re.search(r"Thought:\s*(.+?)(?=\nAction:|\nFinal Answer:|\Z)", response, re.DOTALL)
        if thought_match:
            result["thought"] = thought_match.group(1).strip()
        
        # Check for Final Answer
        final_match = re.search(r"Final Answer:\s*(.+)", response, re.DOTALL)
        if final_match:
            result["final_answer"] = final_match.group(1).strip()
            return result
        
        # Extract Action
        action_match = re.search(r"Action:\s*(.+?)(?:\n|$)", response)
        if action_match:
            result["action"] = action_match.group(1).strip()
        
        # Extract Action Input
        input_match = re.search(r"Action Input:\s*(.+?)(?=\nThought:|\nAction:|\Z)", response, re.DOTALL)
        if input_match:
            result["action_input"] = input_match.group(1).strip()
        
        return result
    
    def _execute_tool(self, tool_name: str, action_input: str) -> str:
        """
        Execute a tool by name with the given input.
        
        Args:
            tool_name: Name of the tool to execute
            action_input: JSON string of parameters
            
        Returns:
            Tool output as string
        """
        if tool_name not in self.tools:
            available = ", ".join(self.tools.keys())
            return f"Error: Tool '{tool_name}' not found. Available tools: {available}"
        
        tool = self.tools[tool_name]
        
        try:
            # Parse input parameters
            if action_input.strip().startswith("{"):
                params = json.loads(action_input)
            else:
                params = {"input": action_input}
            
            # Execute the tool
            result = tool.execute(**params)
            return str(result)
            
        except json.JSONDecodeError:
            return tool.execute(input=action_input)
        except Exception as e:
            logger.error("Tool execution failed", tool=tool_name, error=str(e))
            return f"Error executing {tool_name}: {str(e)}"


class SimulatedLLM:
    """
    Simulated LLM for development and testing without real API calls.
    Generates realistic ReAct responses based on the task.
    """
    
    def __init__(self):
        self.call_count = 0
        self.responses = []
    
    def invoke(self, conversation: list[dict]) -> str:
        """Generate a simulated ReAct response."""
        self.call_count += 1
        
        # Get the original task
        task = ""
        for msg in conversation:
            if msg["role"] == "user" and "Task:" in msg["content"]:
                task = msg["content"].split("Task:")[-1].strip().split("\n")[0]
                break
        
        # Check if we have observations (meaning we've already done steps)
        has_observations = any("Observation:" in msg["content"] for msg in conversation if msg["role"] == "user")
        
        # Generate contextual responses based on task keywords
        task_lower = task.lower()
        
        if not has_observations:
            # First step — gather information
            if "docker" in task_lower or "container" in task_lower:
                return self._docker_step_1()
            elif "kubernetes" in task_lower or "pod" in task_lower or "k8s" in task_lower:
                return self._k8s_step_1()
            elif "github" in task_lower or "ci" in task_lower or "pipeline" in task_lower:
                return self._github_step_1()
            elif "security" in task_lower or "vulnerab" in task_lower or "scan" in task_lower:
                return self._security_step_1()
            elif "monitor" in task_lower or "metric" in task_lower or "health" in task_lower:
                return self._monitoring_step_1()
            elif "cost" in task_lower or "spend" in task_lower or "cloud" in task_lower:
                return self._cost_step_1()
            elif "terraform" in task_lower or "infra" in task_lower:
                return self._terraform_step_1()
            else:
                return self._generic_step_1(task)
        else:
            # Second step — provide final answer
            return self._generate_final_answer(task)
    
    def _docker_step_1(self) -> str:
        return """Thought: I need to check the Docker containers to assess their status. Let me list all running containers first.
Action: list_containers
Action Input: {"all": false}"""
    
    def _k8s_step_1(self) -> str:
        return """Thought: I need to check the Kubernetes pod health. Let me get the status of all pods in the cluster.
Action: get_pods
Action Input: {"namespace": "default"}"""
    
    def _github_step_1(self) -> str:
        return """Thought: I need to check the CI/CD pipeline status. Let me look at the recent GitHub Actions runs.
Action: get_ci_status
Action Input: {"repo": "main-app"}"""
    
    def _security_step_1(self) -> str:
        return """Thought: I need to run a security scan to check for vulnerabilities. Let me scan the Docker images first.
Action: scan_docker_image
Action Input: {"image": "main-app:latest", "severity": "HIGH,CRITICAL"}"""
    
    def _monitoring_step_1(self) -> str:
        return """Thought: I need to check the system metrics to assess overall health. Let me query Prometheus for key metrics.
Action: query_prometheus
Action Input: {"query": "up", "description": "Check service health"}"""
    
    def _cost_step_1(self) -> str:
        return """Thought: I need to analyze cloud costs. Let me gather the current spending data.
Action: get_cloud_costs
Action Input: {"period": "monthly"}"""
    
    def _terraform_step_1(self) -> str:
        return """Thought: I need to check the infrastructure state. Let me review the current Terraform state.
Action: get_terraform_state
Action Input: {"workspace": "default"}"""
    
    def _generic_step_1(self, task: str) -> str:
        return f"""Thought: I need to analyze this request: "{task}". Let me start by checking the system health.
Action: check_service_health
Action Input: {{"service": "all"}}"""
    
    def _generate_final_answer(self, task: str) -> str:
        task_lower = task.lower()
        
        if "docker" in task_lower or "container" in task_lower:
            return """Thought: I now have enough information from the Docker container analysis.
Final Answer: 🐳 **Docker Container Health Report**

**Summary:** All 4 containers are running healthy.

| Container | Status | CPU | Memory |
|-----------|--------|-----|--------|
| api-server | ✅ Running | 12% | 256MB |
| postgres-db | ✅ Running | 5% | 512MB |
| redis-cache | ✅ Running | 2% | 64MB |
| nginx-proxy | ✅ Running | 1% | 32MB |

**Total Resources:** CPU: 20% | Memory: 864MB
**Uptime:** All containers running for 72+ hours with no restarts.
**Recommendation:** System is healthy. No action required."""

        elif "kubernetes" in task_lower or "pod" in task_lower:
            return """Thought: I now have enough information from the Kubernetes cluster analysis.
Final Answer: ☸️ **Kubernetes Cluster Health Report**

**Cluster Status:** ✅ Healthy — 3/3 nodes ready

| Pod | Status | Restarts | Age |
|-----|--------|----------|-----|
| api-server-7d8f9c-x2k4t | ✅ Running | 0 | 3d |
| worker-5c6d7e-m9n2p | ✅ Running | 0 | 3d |
| scheduler-4b5c6d-q8r1s | ⚠️ Running | 1 | 5d |

**Note:** scheduler pod has 1 restart in the last 5 days. This is within normal parameters but should be monitored.
**Resource Usage:** CPU: 34% | Memory: 68% across all nodes.
**Recommendation:** Cluster is healthy overall. Monitor the scheduler pod for additional restarts."""

        elif "security" in task_lower or "scan" in task_lower:
            return """Thought: I now have the security scan results.
Final Answer: 🛡️ **Security Scan Report**

**Image Scanned:** main-app:latest
**Scan Engine:** Trivy v0.50.0

| Severity | Count | Status |
|----------|-------|--------|
| Critical | 0 | ✅ Clear |
| High | 2 | ⚠️ Found |
| Medium | 5 | ℹ️ Info |
| Low | 12 | ℹ️ Info |

**High Severity Findings:**
1. CVE-2024-1234 — openssl 3.0.2: Buffer overflow vulnerability → **Upgrade to 3.0.14**
2. CVE-2024-5678 — libcurl 7.88: Information disclosure → **Upgrade to 7.88.1**

**Recommendation:** Update base image dependencies. Run `pip install --upgrade openssl` and rebuild the container."""

        else:
            return f"""Thought: I now have enough information to provide a comprehensive answer.
Final Answer: ✅ **DevOps Agent Analysis Complete**

**Task:** {task}

**System Health Overview:**
- 🐳 Docker: 4/4 containers running healthy
- ☸️ Kubernetes: 3/3 nodes ready, 12 pods active
- 📊 Metrics: CPU 34% | Memory 68% | Error Rate 0.12%
- 🔄 CI/CD: All pipelines passing
- 🛡️ Security: No critical vulnerabilities

**Current Status:** All systems operational. No immediate action required.
**Recommendation:** Continue routine monitoring. Next scheduled maintenance in 48 hours."""
