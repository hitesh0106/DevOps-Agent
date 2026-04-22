"""
DevOps Agent — Base Tool Class
=================================
Abstract base class for all agent tools with built-in
parameter validation, execution tracking, and error handling.
"""

import time
from abc import ABC, abstractmethod
from typing import Any, Optional

from config.logging_config import get_logger
from config.constants import ToolCategory, RiskLevel

logger = get_logger(__name__)


class BaseTool(ABC):
    """
    Abstract base for all DevOps Agent tools.

    Every tool must define:
    - name: unique identifier
    - description: what the tool does (shown to the LLM)
    - category: ToolCategory enum value
    - risk_level: RiskLevel enum value
    - execute(**kwargs): the actual implementation
    """

    name: str = ""
    description: str = ""
    category: ToolCategory = ToolCategory.SHELL
    risk_level: RiskLevel = RiskLevel.SAFE
    parameters_schema: str = "{}"

    def __init__(self, simulation_mode: bool = True):
        self.simulation_mode = simulation_mode
        self.execution_count = 0
        self.total_execution_time = 0.0

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute the tool with the given parameters."""
        pass

    def run(self, **kwargs) -> dict:
        """
        Run the tool with timing, logging, and error handling.

        Returns:
            dict with keys: success, result, duration_ms, error
        """
        start = time.time()
        self.execution_count += 1

        try:
            result = self.execute(**kwargs)
            duration_ms = (time.time() - start) * 1000
            self.total_execution_time += duration_ms

            logger.info(
                "Tool executed",
                tool=self.name,
                duration_ms=round(duration_ms, 2),
                simulation=self.simulation_mode,
            )

            return {
                "success": True,
                "result": result,
                "duration_ms": round(duration_ms, 2),
                "error": None,
            }
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            logger.error("Tool execution failed", tool=self.name, error=str(e))
            return {
                "success": False,
                "result": None,
                "duration_ms": round(duration_ms, 2),
                "error": str(e),
            }

    def validate_params(self, **kwargs) -> bool:
        """Override to add parameter validation."""
        return True

    def __repr__(self) -> str:
        return f"<Tool:{self.name} category={self.category.value} risk={self.risk_level.value}>"
