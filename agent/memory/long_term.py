
import uuid
from datetime import datetime, timezone
from typing import Optional

from config.logging_config import get_logger
from config.settings import settings

logger = get_logger(__name__)


class LongTermMemory:
    """
    Long-term memory backed by ChromaDB vector store.

    Stores past task resolutions so the agent can learn from
    previous incidents and apply similar fixes.

    Features:
    - Semantic similarity search via embeddings
    - Persistent storage across sessions
    - Metadata filtering (by tool, success status, date)
    """

    def __init__(self, collection_name: str = "incident_history",
                 persist_dir: str = "./data/chromadb"):
        self.collection_name = collection_name
        self.persist_dir = persist_dir
        self._collection = None
        self._client = None

        self._init_store()

    def _init_store(self):
        """Initialize ChromaDB client and collection."""
        if settings.simulation_mode:
            logger.info("Long-term memory: simulation mode (in-memory store)")
            self._memories: list[dict] = []
            return

        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings

            self._client = chromadb.Client(ChromaSettings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=self.persist_dir,
                anonymized_telemetry=False,
            ))
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "DevOps Agent incident history"},
            )
            logger.info(
                "ChromaDB initialized",
                collection=self.collection_name,
                persist_dir=self.persist_dir,
            )
        except Exception as e:
            logger.warning(
                "ChromaDB init failed, using in-memory fallback",
                error=str(e),
            )
            self._memories = []

    def store_resolution(self, task: str, resolution: str,
                         tools_used: list[str] = None,
                         success: bool = True) -> str:
        """
        Store a task resolution in long-term memory.

        Args:
            task: The original task description
            resolution: How the task was resolved
            tools_used: List of tools used during resolution
            success: Whether the resolution was successful

        Returns:
            Memory entry ID
        """
        entry_id = str(uuid.uuid4())[:12]
        metadata = {
            "task": task,
            "resolution": resolution,
            "tools_used": ",".join(tools_used or []),
            "success": str(success),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if self._collection is not None:
            try:
                self._collection.add(
                    documents=[f"{task}\n\nResolution: {resolution}"],
                    metadatas=[metadata],
                    ids=[entry_id],
                )
                logger.info("Resolution stored in ChromaDB", entry_id=entry_id)
            except Exception as e:
                logger.error("Failed to store in ChromaDB", error=str(e))
                self._store_in_memory(entry_id, metadata)
        else:
            self._store_in_memory(entry_id, metadata)

        return entry_id

    def _store_in_memory(self, entry_id: str, metadata: dict):
        """Fallback: store in local list."""
        if not hasattr(self, '_memories'):
            self._memories = []
        self._memories.append({"id": entry_id, **metadata})

    def search_similar(self, query: str, k: int = 3) -> list[dict]:
        """
        Search for similar past incidents using semantic similarity.

        Args:
            query: Search query (natural language)
            k: Number of results to return

        Returns:
            List of similar incident dicts
        """
        if self._collection is not None:
            try:
                results = self._collection.query(
                    query_texts=[query],
                    n_results=min(k, self._collection.count() or 1),
                )
                if results and results["metadatas"]:
                    return results["metadatas"][0]
            except Exception as e:
                logger.warning("ChromaDB search failed", error=str(e))

        # Fallback: simple keyword search in memory
        if hasattr(self, '_memories'):
            query_lower = query.lower()
            scored = []
            for mem in self._memories:
                task_text = mem.get("task", "").lower()
                score = sum(1 for word in query_lower.split() if word in task_text)
                if score > 0:
                    scored.append((score, mem))
            scored.sort(key=lambda x: x[0], reverse=True)
            return [item[1] for item in scored[:k]]

        return []

    def count(self) -> int:
        """Return the number of stored memories."""
        if self._collection is not None:
            try:
                return self._collection.count()
            except Exception:
                pass
        return len(getattr(self, '_memories', []))

    def clear(self) -> None:
        """Clear all long-term memories."""
        if self._collection is not None:
            try:
                self._client.delete_collection(self.collection_name)
                self._collection = self._client.get_or_create_collection(
                    name=self.collection_name,
                )
            except Exception as e:
                logger.error("Failed to clear ChromaDB", error=str(e))
        if hasattr(self, '_memories'):
            self._memories.clear()
        logger.info("Long-term memory cleared")
