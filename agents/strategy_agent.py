"""
Strategy Agent — ML strategist that generates ranked competition approaches.

This is the third agent in the pipeline. It reads competition metadata
and data profile from session state, then generates ranked ML strategies
for the user to review and approve.

Concepts demonstrated:
  - Multi-Agent Systems (ADK) — Specialized sub-agent
  - Agent Skills — Uses the strategy_ranker skill
  - Sessions — Reads from prior agents' state, writes strategies
  - Human-in-the-Loop — Strategies require user approval before
    the Code Agent generates code
"""

from typing import Any

from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext

from context.session_manager import SESSION_KEYS
from mcp_servers.file_server import write_report
from skills.strategy_ranker import (
    format_strategies_as_text,
    get_strategies_for_type,
    rank_strategies,
)


def _get_session_context(tool_context: ToolContext) -> dict[str, Any]:
    """
    Retrieves competition metadata and data profile from session state.

    Returns the context that prior agents (Scraper + Data) have written
    to session state. This provides the information needed to generate
    relevant strategies.

    Returns:
        Dictionary with competition_metadata and data_profile from
        session state. Either or both may be None if prior agents
        haven't run yet.
    """
    metadata = tool_context.state.get(SESSION_KEYS["competition_metadata"])
    data_profile = tool_context.state.get(SESSION_KEYS["data_profile"])

    return {
        "competition_metadata": metadata,
        "data_profile": data_profile,
        "has_metadata": metadata is not None,
        "has_profile": data_profile is not None,
    }


def _generate_strategies(
    competition_type: str,
    dataset_rows: int,
    num_features: int,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """
    Generates ranked ML strategy recommendations based on competition info.

    Uses the strategy_ranker skill to produce template-based strategies,
    then ranks them based on dataset characteristics.

    Args:
        competition_type: Type of competition
            (e.g., 'binary_classification', 'regression')
        dataset_rows: Number of rows in the training dataset
        num_features: Number of features in the dataset

    Returns:
        Ranked list of strategy recommendations with details.
    """
    # Get strategy templates for this competition type
    templates = get_strategies_for_type(competition_type)

    # Rank based on dataset characteristics
    ranked = rank_strategies(
        templates,
        dataset_size=dataset_rows,
        num_features=num_features,
    )

    # Save to session state
    tool_context.state[SESSION_KEYS["strategies"]] = ranked

    return {
        "num_strategies": len(ranked),
        "strategies": ranked,
        "formatted_text": format_strategies_as_text(ranked),
    }


def _save_strategy_report(
    report_content: str, tool_context: ToolContext
) -> dict[str, Any]:
    """
    Saves the strategy report as a markdown file.

    Args:
        report_content: The full markdown content of the strategy report

    Returns:
        Confirmation with file path.
    """
    return write_report(report_content, "strategy_report.md")


def _approve_strategy(
    strategy_rank: int,
    user_modifications: str,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """
    Records the user's strategy choice and any modifications.

    Call this AFTER the user has reviewed the strategies and chosen one
    (possibly with modifications). This saves the approved strategy to
    session state so the Code Agent can generate code for it.

    Args:
        strategy_rank: The rank number of the chosen strategy (1, 2, or 3)
        user_modifications: Any modifications the user requested
            (e.g., 'also add fare binning', 'use XGBoost instead of LightGBM')
            Pass empty string if no modifications.

    Returns:
        Confirmation that the strategy was approved and saved.
    """
    strategies = tool_context.state.get(SESSION_KEYS["strategies"], [])

    # Find the chosen strategy by rank
    chosen = None
    for s in strategies:
        if s.get("rank") == strategy_rank:
            chosen = dict(s)  # Copy to avoid mutation
            break

    if chosen is None:
        return {
            "status": "error",
            "message": (
                f"Strategy #{strategy_rank} not found. "
                f"Available ranks: {[s.get('rank') for s in strategies]}"
            ),
        }

    # Add user modifications
    chosen["user_modifications"] = user_modifications
    chosen["approved"] = True

    # Save to session state
    tool_context.state[SESSION_KEYS["approved_strategy"]] = chosen

    return {
        "status": "approved",
        "strategy_name": chosen["name"],
        "strategy_rank": strategy_rank,
        "modifications": user_modifications or "None",
        "message": (
            f"Strategy #{strategy_rank} '{chosen['name']}' approved! "
            "The Code Agent can now generate baseline code."
        ),
    }


# Define the Strategy Agent
strategy_agent = LlmAgent(
    name="strategy_agent",
    model="gemini-2.5-flash",
    instruction="""You are the ML Strategy Agent for KaggleBot.

Your role is to generate ranked ML strategy recommendations based on
the competition metadata and data profile from prior agents.

## Your Workflow

1. **Gather context**: Call `get_session_context` to read what the
   Scraper Agent and Data Agent discovered. Use this to understand
   the competition type, dataset characteristics, and known insights.

2. **Generate strategies**: Call `generate_strategies` with the
   competition type, dataset size, and feature count. This produces
   ranked strategy templates.

3. **Present to user**: Present the ranked strategies clearly and ask
   the user which strategy they'd like to proceed with. You may also
   suggest modifications based on the competition-specific insights.

4. **CRITICAL — Wait for user approval**: Do NOT auto-approve.
   Present the strategies and wait for the user to choose one.
   The user may:
   - Approve a strategy as-is: "Go with strategy 1"
   - Approve with modifications: "Strategy 1, but use XGBoost"
   - Ask for alternatives: "What about neural networks?"

5. **Record approval**: Once the user approves, call `approve_strategy`
   with the chosen rank and any modifications.

6. **Save report**: Call `save_strategy_report` with a comprehensive
   markdown report of all strategies and the user's choice.

## Presentation Format

For each strategy, present:
- 📋 **Strategy #N: [Name]**
- 🔧 **Models**: [Model list]
- 📊 **Expected Score**: [Range]
- ⚡ **Effort**: [Low/Medium/High] | **Risk**: [Low/Medium/High]
- Key preprocessing and feature engineering steps

## IMPORTANT: Human-in-the-Loop

You MUST wait for the user to explicitly approve a strategy before
calling `approve_strategy`. Never auto-approve. This is a safety
mechanism — the user's judgment about compute budget, time constraints,
and domain expertise is irreplaceable.

After approval, confirm the choice and mention that the Code Agent
can now generate baseline code.""",
    tools=[
        _get_session_context,
        _generate_strategies,
        _save_strategy_report,
        _approve_strategy,
    ],
)
