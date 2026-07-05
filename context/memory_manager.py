"""
Memory Manager — Long-term memory storage and retrieval.

Provides persistent memory across sessions so KaggleBot can learn
from past competition analyses and apply that knowledge to new ones.

Memory is organized by competition type and stored as structured
key-value pairs with metadata (timestamp, source, confidence).

Concept demonstrated: Agent Skills (memory/context management) —
Persistent knowledge that improves agent performance over time.
"""

import json
import os
import time
from typing import Any


# Default memory store file location
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_FILE = os.path.join(_PROJECT_ROOT, "output", "memory_store.json")


class MemoryManager:
    """
    Manages long-term memory for KaggleBot.

    Memory entries are structured as:
    {
        "key": "unique_identifier",
        "category": "strategy|feature_engineering|data_issue|model_performance",
        "competition_type": "classification|regression|etc",
        "content": "The actual learning/insight",
        "metadata": {
            "source_competition": "titanic",
            "timestamp": 1234567890,
            "confidence": 0.8,
            "times_used": 0,
        }
    }
    """

    def __init__(self, filepath: str = MEMORY_FILE):
        self.filepath = filepath
        self._memories: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        """Loads memories from disk."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self._memories = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._memories = []
        else:
            self._memories = []

    def _save(self) -> None:
        """Persists memories to disk."""
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self._memories, f, indent=2)

    def store(
        self,
        key: str,
        content: str,
        category: str,
        competition_type: str = "general",
        source_competition: str = "",
        confidence: float = 0.8,
    ) -> dict[str, str]:
        """
        Stores a new memory entry.

        Args:
            key: Unique identifier for this memory
            content: The learning/insight to remember
            category: One of 'strategy', 'feature_engineering',
                      'data_issue', 'model_performance'
            competition_type: The type of competition this applies to
            source_competition: Which competition this was learned from
            confidence: How confident we are in this insight (0-1)

        Returns:
            Confirmation of storage.
        """
        # Check for duplicates — update if key exists
        for i, mem in enumerate(self._memories):
            if mem["key"] == key:
                self._memories[i]["content"] = content
                self._memories[i]["metadata"]["timestamp"] = time.time()
                self._memories[i]["metadata"]["confidence"] = confidence
                self._save()
                return {"status": "updated", "key": key}

        entry = {
            "key": key,
            "category": category,
            "competition_type": competition_type,
            "content": content,
            "metadata": {
                "source_competition": source_competition,
                "timestamp": time.time(),
                "confidence": confidence,
                "times_used": 0,
            },
        }

        self._memories.append(entry)
        self._save()
        return {"status": "stored", "key": key}

    def retrieve(
        self,
        competition_type: str | None = None,
        category: str | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Retrieves relevant memories, filtered by type and category.

        Args:
            competition_type: Filter by competition type (optional)
            category: Filter by category (optional)
            limit: Maximum memories to return

        Returns:
            List of matching memory entries, sorted by relevance.
        """
        results = []

        for mem in self._memories:
            score = 0

            # Type match
            if competition_type:
                if mem["competition_type"] == competition_type:
                    score += 10
                elif mem["competition_type"] == "general":
                    score += 5  # General memories are always somewhat relevant

            # Category match
            if category:
                if mem["category"] == category:
                    score += 10

            # Confidence weighting
            score += mem["metadata"].get("confidence", 0.5) * 5

            # Recency bonus (memories from last 7 days get a boost)
            age_days = (time.time() - mem["metadata"].get("timestamp", 0)) / 86400
            if age_days < 7:
                score += 3

            if score > 0 or (not competition_type and not category):
                mem_copy = dict(mem)
                mem_copy["relevance_score"] = score
                results.append(mem_copy)

        # Sort by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)

        # Update usage count for returned memories
        returned_keys = {r["key"] for r in results[:limit]}
        for mem in self._memories:
            if mem["key"] in returned_keys:
                mem["metadata"]["times_used"] = (
                    mem["metadata"].get("times_used", 0) + 1
                )
        self._save()

        return results[:limit]

    def get_all(self) -> list[dict[str, Any]]:
        """Returns all stored memories."""
        return list(self._memories)

    def clear(self) -> dict[str, str]:
        """Clears all memories."""
        self._memories = []
        self._save()
        return {"status": "cleared"}

    def get_stats(self) -> dict[str, Any]:
        """Returns statistics about the memory store."""
        categories = {}
        types = {}
        for mem in self._memories:
            cat = mem.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
            typ = mem.get("competition_type", "unknown")
            types[typ] = types.get(typ, 0) + 1

        return {
            "total_memories": len(self._memories),
            "by_category": categories,
            "by_type": types,
            "filepath": self.filepath,
        }


# Singleton instance for the application
_memory_manager: MemoryManager | None = None


def get_memory_manager() -> MemoryManager:
    """Returns the singleton MemoryManager instance."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager
