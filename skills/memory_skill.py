"""
Memory Skill — Agent-facing memory tools for cross-session learning.

Wraps the MemoryManager as ADK-compatible tool functions that agents
can call to store insights and retrieve past learnings.

Concept demonstrated: Agent Skills — Memory/context management
as a reusable capability loaded by the orchestrator.
"""

from typing import Any

from google.adk.tools import ToolContext

from context.memory_manager import get_memory_manager


def store_learning(
    key: str,
    content: str,
    category: str,
    competition_type: str,
    source_competition: str,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """
    Stores a learning/insight to long-term memory for future sessions.

    Call this when you discover something valuable that could help
    analyze similar competitions in the future.

    Args:
        key: Unique identifier (e.g., 'titanic_feature_engineering')
        content: The insight to remember (be specific and actionable)
        category: One of: 'strategy', 'feature_engineering',
                  'data_issue', 'model_performance'
        competition_type: e.g., 'binary_classification', 'regression'
        source_competition: Which competition this came from
            (e.g., 'titanic')

    Returns:
        Confirmation of storage.
    """
    manager = get_memory_manager()
    result = manager.store(
        key=key,
        content=content,
        category=category,
        competition_type=competition_type,
        source_competition=source_competition,
    )
    return result


def recall_learnings(
    competition_type: str,
    category: str,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """
    Retrieves relevant past learnings from long-term memory.

    Call this at the start of a new analysis to see if we have
    useful knowledge from past competition analyses.

    Args:
        competition_type: Type of the current competition
            (e.g., 'binary_classification', 'regression')
        category: What kind of knowledge to look for.
            One of: 'strategy', 'feature_engineering',
            'data_issue', 'model_performance', or '' for all.

    Returns:
        List of relevant past learnings with relevance scores.
    """
    manager = get_memory_manager()

    memories = manager.retrieve(
        competition_type=competition_type if competition_type else None,
        category=category if category else None,
        limit=5,
    )

    return {
        "num_memories": len(memories),
        "memories": [
            {
                "key": m["key"],
                "content": m["content"],
                "category": m["category"],
                "competition_type": m["competition_type"],
                "source": m["metadata"].get("source_competition", ""),
                "confidence": m["metadata"].get("confidence", 0),
                "relevance": m.get("relevance_score", 0),
            }
            for m in memories
        ],
    }


def get_memory_stats(tool_context: ToolContext) -> dict[str, Any]:
    """
    Returns statistics about what's stored in long-term memory.

    Useful for understanding what the agent has learned so far.

    Returns:
        Total memories, breakdown by category and type.
    """
    manager = get_memory_manager()
    return manager.get_stats()
