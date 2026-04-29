
from enum import Enum
from typing import Optional, Callable


class StageStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class PipelineStage:
    """A single stage in a CI/CD pipeline."""

    def __init__(self, name: str, command: str = "", description: str = "",
                 timeout: int = 300, allow_failure: bool = False,
                 executor: Optional[Callable] = None):
        self.name = name
        self.command = command
        self.description = description or name
        self.timeout = timeout
        self.allow_failure = allow_failure
        self.status = StageStatus.PENDING
        self._executor = executor

    def execute(self) -> str:
        """Execute the stage command."""
        if self._executor:
            return self._executor()
        if self.command:
            import subprocess
            result = subprocess.run(
                self.command, shell=True, capture_output=True,
                text=True, timeout=self.timeout,
            )
            if result.returncode != 0 and not self.allow_failure:
                raise RuntimeError(f"Stage '{self.name}' failed: {result.stderr}")
            return result.stdout
        return f"Stage '{self.name}' executed (no command)"

    def to_dict(self) -> dict:
        return {
            "name": self.name, "command": self.command,
            "description": self.description, "status": self.status.value,
            "timeout": self.timeout, "allow_failure": self.allow_failure,
        }
