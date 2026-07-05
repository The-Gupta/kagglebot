"""
Session Manager — Manages session state schema and handoff between agents.

Session state flows:
  Scraper Agent → writes competition_metadata
  Data Agent    → writes data_profile
  Strategy Agent → writes strategies
  HITL          → writes approved_strategy
  Code Agent    → writes generated_code

Each agent reads from prior agents' state and writes its own output.
"""

from typing import Any

# Session state keys — used by agents to read/write structured state
SESSION_KEYS = {
    "competition_metadata": "competition_metadata",
    "data_profile": "data_profile",
    "strategies": "strategies",
    "approved_strategy": "approved_strategy",
    "generated_code": "generated_code",
    "evaluation_report": "evaluation_report",
    "trace_id": "trace_id",
}


def get_initial_state() -> dict[str, Any]:
    """Returns the initial session state schema with empty values."""
    return {
        SESSION_KEYS["competition_metadata"]: None,
        SESSION_KEYS["data_profile"]: None,
        SESSION_KEYS["strategies"]: None,
        SESSION_KEYS["approved_strategy"]: None,
        SESSION_KEYS["generated_code"]: None,
        SESSION_KEYS["evaluation_report"]: None,
        SESSION_KEYS["trace_id"]: None,
    }


def validate_state_key(key: str) -> bool:
    """Validates that a key is a known session state key."""
    return key in SESSION_KEYS.values()


def get_state_summary(state: dict[str, Any]) -> dict[str, str]:
    """Returns a human-readable summary of what's populated in session state."""
    summary = {}
    for display_name, key in SESSION_KEYS.items():
        value = state.get(key)
        if value is None:
            summary[display_name] = "⬜ Not set"
        elif isinstance(value, dict):
            summary[display_name] = f"✅ Set ({len(value)} keys)"
        elif isinstance(value, list):
            summary[display_name] = f"✅ Set ({len(value)} items)"
        elif isinstance(value, str):
            summary[display_name] = f"✅ Set ({len(value)} chars)"
        else:
            summary[display_name] = f"✅ Set ({type(value).__name__})"
    return summary
