"""
DevOps Agent — Sandboxed Execution
=====================================
Provides isolated execution environments for untrusted commands.
"""

import json
import subprocess
from typing import Optional
from config.logging_config import get_logger

logger = get_logger(__name__)


class Sandbox:
    """
    Sandboxed command execution with resource limits.

    In production, this uses Docker containers for isolation.
    In simulation mode, commands are captured but not executed.
    """

    def __init__(self, simulation_mode: bool = True):
        self.simulation_mode = simulation_mode
        self.execution_log: list[dict] = []

    def execute(self, command: str, timeout: int = 30,
                max_memory_mb: int = 512,
                network: bool = False) -> dict:
        """
        Execute a command in a sandboxed environment.

        Args:
            command: Command to execute
            timeout: Maximum execution time in seconds
            max_memory_mb: Memory limit in MB
            network: Whether to allow network access

        Returns:
            dict with stdout, stderr, returncode, duration
        """
        log_entry = {"command": command, "timeout": timeout, "network": network}

        if self.simulation_mode:
            log_entry["result"] = "simulated"
            self.execution_log.append(log_entry)
            return {
                "stdout": f"[sandbox-sim] Executed: {command}",
                "stderr": "",
                "returncode": 0,
                "sandboxed": True,
                "simulated": True,
            }

        try:
            # In production, use Docker for isolation
            docker_cmd = [
                "docker", "run", "--rm",
                "--memory", f"{max_memory_mb}m",
                "--cpus", "0.5",
                "--pids-limit", "50",
            ]

            if not network:
                docker_cmd.append("--network=none")

            docker_cmd.extend(["python:3.11-slim", "sh", "-c", command])

            result = subprocess.run(
                docker_cmd, capture_output=True, text=True, timeout=timeout,
            )

            log_entry["result"] = "success" if result.returncode == 0 else "failed"
            self.execution_log.append(log_entry)

            return {
                "stdout": result.stdout[:2000],
                "stderr": result.stderr[:500],
                "returncode": result.returncode,
                "sandboxed": True,
            }
        except subprocess.TimeoutExpired:
            log_entry["result"] = "timeout"
            self.execution_log.append(log_entry)
            return {"stdout": "", "stderr": "Command timed out", "returncode": -1, "sandboxed": True}
        except Exception as e:
            log_entry["result"] = "error"
            self.execution_log.append(log_entry)
            return {"stdout": "", "stderr": str(e), "returncode": -1, "sandboxed": True}

    def get_log(self) -> list[dict]:
        """Return the sandbox execution log."""
        return self.execution_log
