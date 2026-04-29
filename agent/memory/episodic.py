
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from config.logging_config import get_logger
from config.settings import settings, BASE_DIR

logger = get_logger(__name__)

DB_PATH = BASE_DIR / "data" / "episodic_memory.db"


class EpisodicMemory:
    """
    Episodic memory — stores structured incident history.

    Each episode records a complete task lifecycle:
    - Task description
    - Steps taken (thought → action → observation)
    - Final result
    - Whether it succeeded or failed

    This helps the agent learn from past experiences.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(DB_PATH)
        self._init_db()

    def _init_db(self):
        """Create the episodes table if it doesn't exist."""
        try:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS episodes (
                    id TEXT PRIMARY KEY,
                    task TEXT NOT NULL,
                    result TEXT,
                    steps TEXT,
                    success INTEGER DEFAULT 0,
                    tools_used TEXT,
                    duration_seconds REAL,
                    created_at TEXT NOT NULL
                )
            """)
            conn.commit()
            conn.close()
            logger.debug("Episodic memory DB initialized", path=self.db_path)
        except Exception as e:
            logger.warning("Episodic memory DB init failed", error=str(e))

    def store_episode(self, task_id: str, task: str, result: str,
                      steps: list[dict] = None, success: bool = True,
                      tools_used: list[str] = None,
                      duration_seconds: float = None) -> None:
        """
        Store a complete task episode.

        Args:
            task_id: Unique task identifier
            task: Task description
            result: Final result/answer
            steps: List of ReAct step dicts
            success: Whether the task succeeded
            tools_used: List of tools invoked
            duration_seconds: Total execution time
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute(
                """INSERT OR REPLACE INTO episodes
                   (id, task, result, steps, success, tools_used, duration_seconds, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    task_id,
                    task,
                    result,
                    json.dumps(steps or []),
                    1 if success else 0,
                    ",".join(tools_used or []),
                    duration_seconds,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            conn.commit()
            conn.close()
            logger.info("Episode stored", task_id=task_id, success=success)
        except Exception as e:
            logger.error("Failed to store episode", error=str(e))

    def get_episode(self, task_id: str) -> Optional[dict]:
        """Retrieve a specific episode by task ID."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute(
                "SELECT * FROM episodes WHERE id = ?", (task_id,)
            )
            row = cursor.fetchone()
            conn.close()
            if row:
                return self._row_to_dict(row)
        except Exception as e:
            logger.error("Failed to get episode", error=str(e))
        return None

    def get_recent(self, limit: int = 10) -> list[dict]:
        """Get the most recent episodes."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute(
                "SELECT * FROM episodes ORDER BY created_at DESC LIMIT ?",
                (limit,),
            )
            rows = cursor.fetchall()
            conn.close()
            return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            logger.error("Failed to get recent episodes", error=str(e))
            return []

    def get_failures(self, limit: int = 10) -> list[dict]:
        """Get recent failed episodes for learning."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute(
                "SELECT * FROM episodes WHERE success = 0 ORDER BY created_at DESC LIMIT ?",
                (limit,),
            )
            rows = cursor.fetchall()
            conn.close()
            return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            logger.error("Failed to get failure episodes", error=str(e))
            return []

    def count(self) -> int:
        """Return the total number of stored episodes."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("SELECT COUNT(*) FROM episodes")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception:
            return 0

    def _row_to_dict(self, row: tuple) -> dict:
        """Convert a database row to a dictionary."""
        return {
            "id": row[0],
            "task": row[1],
            "result": row[2],
            "steps": json.loads(row[3]) if row[3] else [],
            "success": bool(row[4]),
            "tools_used": row[5].split(",") if row[5] else [],
            "duration_seconds": row[6],
            "created_at": row[7],
        }

    def clear(self) -> None:
        """Clear all episodes."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("DELETE FROM episodes")
            conn.commit()
            conn.close()
            logger.info("Episodic memory cleared")
        except Exception as e:
            logger.error("Failed to clear episodic memory", error=str(e))
