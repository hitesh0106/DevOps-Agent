"""
DevOps Agent — Short-Term Memory
==================================
In-memory conversation buffer for the current agent session.
Stores recent thoughts, actions, and observations with auto-truncation.
"""

from datetime import datetime, timezone
from typing import Optional
from collections import deque

from config.logging_config import get_logger

logger = get_logger(__name__)


class MemoryEntry:
    """A single memory entry with metadata."""

    def __init__(self, role: str, content: str, metadata: Optional[dict] = None):
        self.role = role
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


class ShortTermMemory:
    """
    Short-term memory — stores the current session's conversation context.

    Features:
    - Fixed-size buffer with auto-truncation (FIFO)
    - Role-based entries (system, user, assistant, step)
    - Search by role or keyword
    - Token-aware truncation for LLM context windows
    """

    def __init__(self, max_entries: int = 50):
        """
        Args:
            max_entries: Maximum number of entries to retain
        """
        self.max_entries = max_entries
        self._buffer: deque[MemoryEntry] = deque(maxlen=max_entries)
        logger.debug("Short-term memory initialized", max_entries=max_entries)

    def add(self, role: str, content: str, metadata: Optional[dict] = None) -> None:
        """
        Add an entry to short-term memory.

        Args:
            role: Entry role (system, user, assistant, step, observation)
            content: Text content
            metadata: Optional metadata dict
        """
        entry = MemoryEntry(role=role, content=content, metadata=metadata)
        self._buffer.append(entry)
        logger.debug("Memory entry added", role=role, buffer_size=len(self._buffer))

    def get_recent(self, n: int = 10) -> list[dict]:
        """Get the N most recent entries."""
        entries = list(self._buffer)[-n:]
        return [e.to_dict() for e in entries]

    def get_by_role(self, role: str) -> list[dict]:
        """Get all entries matching a specific role."""
        return [e.to_dict() for e in self._buffer if e.role == role]

    def search(self, keyword: str) -> list[dict]:
        """Search entries by keyword (case-insensitive)."""
        keyword_lower = keyword.lower()
        return [
            e.to_dict() for e in self._buffer
            if keyword_lower in e.content.lower()
        ]

    def get_context_string(self, max_chars: int = 4000) -> str:
        """
        Build a context string from recent memory for LLM consumption.

        Args:
            max_chars: Maximum character count for the context string

        Returns:
            Formatted string of recent memory entries
        """
        entries = list(self._buffer)
        lines = []
        total_chars = 0

        for entry in reversed(entries):
            line = f"[{entry.role}] {entry.content}"
            if total_chars + len(line) > max_chars:
                break
            lines.insert(0, line)
            total_chars += len(line)

        return "\n".join(lines)

    def size(self) -> int:
        """Return the number of entries in memory."""
        return len(self._buffer)

    def clear(self) -> None:
        """Clear all memory entries."""
        self._buffer.clear()
        logger.info("Short-term memory cleared")

    def to_dict(self) -> list[dict]:
        """Export all entries as a list of dicts."""
        return [e.to_dict() for e in self._buffer]
