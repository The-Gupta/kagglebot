"""
Strategy Evaluator — LLM-as-Judge for assessing strategy quality.

Uses a separate LLM call with a structured rubric to evaluate the
quality of generated ML strategies. Produces a scored evaluation
report that serves as a confidence signal.

Concept demonstrated: Agent Evaluation — Automated quality assessment
using LLM-as-Judge pattern. If the score is below threshold, the
agent can auto-retry with feedback for self-improvement.
"""

import json
import os
from typing import Any

from google.adk.tools import ToolContext

from context.session_manager import SESSION_KEYS
from evaluation.eval_criteria import (
    STRATEGY_EVAL_RUBRIC,
    compute_weighted_score,
    get_eval_prompt,
)
from mcp_servers.file_server import write_report
from skills.strategy_ranker import format_strategies_as_text


def _build_competition_context(
    metadata: dict[str, Any] | None,
    data_profile: str | None,
) -> str:
    """Builds a competition context summary for the evaluator."""
    parts = []

    if metadata:
        parts.append(f"Competition: {metadata.get('title', 'Unknown')}")
        parts.append(f"Type: {metadata.get('competition_type', 'Unknown')}")
        parts.append(f"Metric: {metadata.get('evaluation_metric', 'Unknown')}")
        parts.append(
            f"Description: {metadata.get('description', 'No description')[:200]}"
        )

    if data_profile:
        parts.append(f"\nData Profile:\n{data_profile[:500]}")

    return "\n".join(parts) if parts else "No competition context available."


def evaluate_strategies(tool_context: ToolContext) -> dict[str, Any]:
    """
    Evaluates the generated strategies using the LLM-as-Judge rubric.

    Reads strategies from session state, builds an evaluation prompt,
    and returns a structured evaluation. Note: In a full implementation,
    this would call the LLM. Here we provide a deterministic evaluation
    based on rubric analysis to avoid extra API calls during demos.

    Returns:
        Evaluation report with per-criterion scores, overall score,
        summary, and improvement suggestions.
    """
    strategies = tool_context.state.get(SESSION_KEYS["strategies"], [])
    metadata = tool_context.state.get(SESSION_KEYS["competition_metadata"])
    data_profile = tool_context.state.get(SESSION_KEYS["data_profile"])

    if not strategies:
        return {
            "status": "error",
            "message": "No strategies found in session state. "
            "Run the Strategy Agent first.",
        }

    # Build the evaluation context
    competition_context = _build_competition_context(metadata, data_profile)
    strategies_text = format_strategies_as_text(strategies)

    # Generate the evaluation prompt (for LLM-as-Judge)
    eval_prompt = get_eval_prompt(strategies_text, competition_context)

    # Deterministic evaluation based on strategy properties
    # (In production, this would be an LLM call)
    scores = _deterministic_evaluate(strategies, metadata)

    overall = compute_weighted_score(
        {k: v["score"] for k, v in scores.items()}
    )

    # Generate improvement suggestions
    suggestions = _generate_suggestions(scores)

    evaluation = {
        "status": "completed",
        "scores": scores,
        "overall_score": overall,
        "max_score": 5.0,
        "pass_threshold": 3.0,
        "passed": overall >= 3.0,
        "summary": _generate_summary(overall, strategies),
        "improvement_suggestions": suggestions,
        "eval_prompt_length": len(eval_prompt),
    }

    # Save to session state
    tool_context.state[SESSION_KEYS["evaluation_report"]] = evaluation

    return evaluation


def save_evaluation_report(
    tool_context: ToolContext,
) -> dict[str, Any]:
    """
    Saves the evaluation report to a file.

    Returns:
        Confirmation with file path.
    """
    evaluation = tool_context.state.get(SESSION_KEYS["evaluation_report"])
    if not evaluation:
        return {
            "status": "error",
            "message": "No evaluation report found. Run evaluate_strategies first.",
        }

    # Format as markdown
    md_lines = [
        "# Strategy Evaluation Report",
        "",
        f"**Overall Score: {evaluation['overall_score']}/5.0**",
        f"**Status: {'✅ PASSED' if evaluation['passed'] else '❌ BELOW THRESHOLD'}**",
        "",
        "## Per-Criterion Scores",
        "",
        "| Criterion | Score | Weight | Justification |",
        "|---|---|---|---|",
    ]

    for criterion in STRATEGY_EVAL_RUBRIC:
        name = criterion["criterion"]
        weight = f"{criterion['weight'] * 100:.0f}%"
        score_data = evaluation["scores"].get(name, {})
        score = score_data.get("score", "N/A")
        justification = score_data.get("justification", "")
        md_lines.append(f"| {name.title()} | {score}/5 | {weight} | {justification} |")

    md_lines.extend([
        "",
        "## Summary",
        evaluation.get("summary", ""),
        "",
        "## Improvement Suggestions",
    ])

    for suggestion in evaluation.get("improvement_suggestions", []):
        md_lines.append(f"- {suggestion}")

    content = "\n".join(md_lines)
    return write_report(content, "eval_report.md")


def _deterministic_evaluate(
    strategies: list[dict[str, Any]],
    metadata: dict[str, Any] | None,
) -> dict[str, dict[str, Any]]:
    """
    Provides a deterministic evaluation based on strategy properties.

    This is used when we don't want to make an extra LLM call.
    Analyzes the strategies structurally to assign scores.
    """
    scores: dict[str, dict[str, Any]] = {}
    comp_type = metadata.get("competition_type", "unknown") if metadata else "unknown"

    # --- Relevance ---
    type_match = any(
        s.get("model_family") in ("tree_based", "linear", "ensemble")
        for s in strategies
    )
    has_multiple = len(strategies) >= 2
    relevance_score = 3
    if type_match:
        relevance_score += 1
    if has_multiple and comp_type != "unknown":
        relevance_score += 1
    scores["relevance"] = {
        "score": min(relevance_score, 5),
        "justification": (
            "Strategies include appropriate model families for the task."
            if type_match
            else "Limited model family coverage."
        ),
    }

    # --- Feasibility ---
    has_effort = all("effort" in s for s in strategies)
    has_risk = all("risk" in s for s in strategies)
    feasibility_score = 3
    if has_effort:
        feasibility_score += 1
    if has_risk:
        feasibility_score += 1
    scores["feasibility"] = {
        "score": min(feasibility_score, 5),
        "justification": (
            "Effort and risk assessments are provided for all strategies."
            if has_effort and has_risk
            else "Missing effort or risk assessments."
        ),
    }

    # --- Ranking Quality ---
    has_ranking = all("rank" in s for s in strategies)
    has_scores = all("ranking_score" in s for s in strategies)
    ranking_score = 3
    if has_ranking:
        ranking_score += 1
    if has_scores:
        ranking_score += 1
    scores["ranking_quality"] = {
        "score": min(ranking_score, 5),
        "justification": (
            "Strategies are ranked with scoring rationale."
            if has_ranking and has_scores
            else "Ranking exists but could use better justification."
        ),
    }

    # --- Completeness ---
    completeness_items = [
        "preprocessing", "feature_engineering", "validation", "models"
    ]
    coverage = sum(
        1
        for s in strategies
        for item in completeness_items
        if item in s
    ) / (len(strategies) * len(completeness_items))
    completeness_score = max(1, min(5, int(coverage * 5) + 1))
    scores["completeness"] = {
        "score": completeness_score,
        "justification": (
            f"Strategies cover {coverage * 100:.0f}% of expected components."
        ),
    }

    # --- Novelty ---
    has_fe = any("feature_engineering" in s for s in strategies)
    has_diverse_models = len(set(s.get("model_family", "") for s in strategies)) >= 2
    novelty_score = 2
    if has_fe:
        novelty_score += 1
    if has_diverse_models:
        novelty_score += 1
    scores["novelty"] = {
        "score": min(novelty_score, 5),
        "justification": (
            "Strategies include diverse model families and feature engineering."
            if has_fe and has_diverse_models
            else "Could benefit from more creative approaches."
        ),
    }

    return scores


def _generate_suggestions(scores: dict[str, dict[str, Any]]) -> list[str]:
    """Generates improvement suggestions based on low scores."""
    suggestions = []

    for name, data in scores.items():
        if data["score"] <= 3:
            if name == "relevance":
                suggestions.append(
                    "Tailor strategies more specifically to the competition "
                    "metric and dataset characteristics."
                )
            elif name == "feasibility":
                suggestions.append(
                    "Include more detailed effort estimates and computational "
                    "requirements for each strategy."
                )
            elif name == "ranking_quality":
                suggestions.append(
                    "Provide clearer reasoning for why strategies are ranked "
                    "in their current order."
                )
            elif name == "completeness":
                suggestions.append(
                    "Ensure each strategy covers preprocessing, feature "
                    "engineering, validation, and model selection."
                )
            elif name == "novelty":
                suggestions.append(
                    "Add more creative, competition-specific feature "
                    "engineering ideas beyond standard approaches."
                )

    if not suggestions:
        suggestions.append("Strategies look solid! Consider adding an ensembling tier.")

    return suggestions


def _generate_summary(overall: float, strategies: list) -> str:
    """Generates a human-readable evaluation summary."""
    if overall >= 4.5:
        quality = "excellent"
    elif overall >= 3.5:
        quality = "good"
    elif overall >= 3.0:
        quality = "acceptable"
    else:
        quality = "needs improvement"

    return (
        f"Strategy recommendations are {quality} (score: {overall}/5.0). "
        f"Evaluated {len(strategies)} strategies across 5 criteria."
    )
