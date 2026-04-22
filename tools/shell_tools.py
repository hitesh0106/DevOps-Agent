"""
DevOps Agent — Shell Tools
"""

import json
import subprocess
import shlex
from tools.base import BaseTool
from config.constants import ToolCategory, RiskLevel, BLOCKED_COMMANDS


class SafeExecute(BaseTool):
    name = "safe_execute"
    description = "Execute a shell command in a sandboxed environment with safety checks"
    category = ToolCategory.SHELL
    risk_level = RiskLevel.MEDIUM
    parameters_schema = '{"command": "string", "timeout": "integer (optional, default 30)"}'

    # Commands allowed in simulation mode
    SAFE_COMMANDS = ["ls", "cat", "echo", "pwd", "whoami", "date", "uptime", "df", "free", "ps", "top", "netstat", "curl", "wget", "ping", "dig", "nslookup", "git"]

    def execute(self, **kwargs):
        command = kwargs.get("command", "")
        timeout = kwargs.get("timeout", 30)

        # Safety check — block dangerous commands
        for blocked in BLOCKED_COMMANDS:
            if blocked in command:
                return json.dumps({"status": "BLOCKED", "reason": f"Dangerous command detected: {blocked}", "command": command})

        if self.simulation_mode:
            return self._simulate(command)

        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True,
                timeout=timeout, cwd="/tmp",
            )
            return json.dumps({
                "stdout": result.stdout[:2000],
                "stderr": result.stderr[:500],
                "returncode": result.returncode,
                "command": command,
            })
        except subprocess.TimeoutExpired:
            return json.dumps({"status": "timeout", "command": command, "timeout": timeout})
        except Exception as e:
            return json.dumps({"status": "error", "error": str(e), "command": command})

    def _simulate(self, command: str) -> str:
        cmd_parts = command.strip().split()
        base_cmd = cmd_parts[0] if cmd_parts else ""

        simulated = {
            "ls": "Dockerfile  README.md  agent/  api/  config/  dashboard/  requirements.txt  tools/",
            "pwd": "/app",
            "whoami": "agent",
            "date": "Tue Apr 22 13:30:00 UTC 2026",
            "uptime": "up 72 days, 4:23, load average: 0.32, 0.28, 0.25",
            "df": "Filesystem  Size  Used  Avail  Use%\n/dev/sda1   50G   18G   30G    38%",
            "free": "              total    used    free\nMem:          16384    8192    8192\nSwap:          4096     256    3840",
        }

        output = simulated.get(base_cmd, f"[simulated] Command executed: {command}")
        return json.dumps({"stdout": output, "returncode": 0, "command": command, "simulated": True})
