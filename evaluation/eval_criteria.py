"""
Eval Criteria — Rubric definitions for LLM-as-Judge strategy evaluation.

Defines the scoring criteria, weights, and prompt templates used by
the Strategy Evaluator to assess the quality of generated strategies.

Concept demonstrated: Agent Evaluation — Structured evaluation
rubric that enables automated quality assessment.
"""

from typing import Any


# Evaluation rubric for strategy quality
STRATEGY_EVAL_RUBRIC = [
    {
        "criterion": "relevance",
        "weight": 0.25,
        "description": (
            "Do the strategies match the competition type and evaluation "
            "metric? Are they appropriate for the dataset characteristics?"
        ),
        "scoring_guide": {
            1: "Strategies don't match the competition type at all",
            2: "Strategies partially match but miss key aspects",
            3: "Strategies match the type but ignore metric specifics",
            4: "Strategies match type and metric, with good awareness",
            5: "Perfect match — strategies are tailored to the specific competition",
        },
    },
    {
        "criterion": "feasibility",
        "weight": 0.25,
        "description": (
            "Are the strategies achievable given the dataset size, feature "
            "types, and computational constraints? Are the effort and risk "
            "assessments realistic?"
        ),
        "scoring_guide": {
            1: "Strategies are completely unrealistic for this dataset",
            2: "Major feasibility issues (e.g., deep learning on 100 rows)",
            3: "Mostly feasible with some questionable choices",
            4: "All strategies are feasible with accurate effort estimates",
            5: "Perfectly calibrated to dataset size and complexity",
        },
    },
    {
        "criterion": "ranking_quality",
        "weight": 0.20,
        "description": (
            "Is the #1 strategy genuinely the best starting point? "
            "Is the ordering logical and well-reasoned?"
        ),
        "scoring_guide": {
            1: "Ranking is inverted — worst strategy is ranked first",
            2: "Ranking has major issues — a better option is available",
            3: "Reasonable ranking but arguable ordering",
            4: "Good ranking with clear reasoning for each position",
            5: "Optimal ranking — #1 is clearly the best starting point",
        },
    },
    {
        "criterion": "completeness",
        "weight": 0.15,
        "description": (
            "Does the strategy cover all necessary aspects: preprocessing, "
            "feature engineering, model selection, validation, and submission?"
        ),
        "scoring_guide": {
            1: "Missing most required components",
            2: "Covers only model selection, missing preprocessing/validation",
            3: "Covers most aspects but missing feature engineering or validation",
            4: "Comprehensive coverage with minor gaps",
            5: "Complete — covers every aspect of the ML pipeline",
        },
    },
    {
        "criterion": "novelty",
        "weight": 0.15,
        "description": (
            "Does it go beyond 'just use XGBoost'? Any creative feature "
            "engineering ideas, unusual model choices, or innovative "
            "validation strategies?"
        ),
        "scoring_guide": {
            1: "Completely generic — no domain-specific insights",
            2: "Mostly generic with one minor insight",
            3: "Some creative ideas but mostly standard approaches",
            4: "Good mix of standard and creative approaches",
            5: "Highly creative with unique, competition-specific insights",
        },
    },
]


def get_rubric_text() -> str:
    """Returns the full rubric as formatted text for LLM evaluation."""
    lines = ["# Strategy Evaluation Rubric\n"]

    for criterion in STRATEGY_EVAL_RUBRIC:
        lines.append(
            f"## {criterion['criterion'].title()} "
            f"(Weight: {criterion['weight'] * 100:.0f}%)"
        )
        lines.append(f"{criterion['description']}\n")
        lines.append("Scoring guide:")
        for score, guide in criterion["scoring_guide"].items():
            lines.append(f"  {score}/5 — {guide}")
        lines.append("")

    return "\n".join(lines)


def get_eval_prompt(
    strategies_text: str,
    competition_context: str,
) -> str:
    """
    Generates the full evaluation prompt for the LLM judge.

    Args:
        strategies_text: The formatted strategy recommendations to evaluate
        competition_context: Summary of competition metadata and data profile

    Returns:
        Complete evaluation prompt.
    """
    rubric = get_rubric_text()

    return f"""You are an expert ML competition judge evaluating strategy recommendations.

## Competition Context
{competition_context}

## Strategies to Evaluate
{strategies_text}

## Evaluation Rubric
{rubric}

## Instructions
1. Score EACH criterion from 1 to 5 based on the scoring guide above.
2. Provide a brief justification for each score.
3. Calculate the weighted overall score.
4. Provide actionable feedback for improvement.

## Required Output Format (JSON)
Return your evaluation as a JSON object with this exact structure:
{{
    "scores": {{
        "relevance": {{"score": <1-5>, "justification": "<why>"}},
        "feasibility": {{"score": <1-5>, "justification": "<why>"}},
        "ranking_quality": {{"score": <1-5>, "justification": "<why>"}},
        "completeness": {{"score": <1-5>, "justification": "<why>"}},
        "novelty": {{"score": <1-5>, "justification": "<why>"}}
    }},
    "overall_score": <weighted average>,
    "summary": "<1-2 sentence summary>",
    "improvement_suggestions": ["<suggestion 1>", "<suggestion 2>"]
}}
"""


def compute_weighted_score(scores: dict[str, int]) -> float:
    """
    Computes the weighted overall score from individual criterion scores.

    Args:
        scores: Dictionary mapping criterion names to scores (1-5)

    Returns:
        Weighted average score (1.0 - 5.0)
    """
    total = 0.0
    total_weight = 0.0

    for criterion in STRATEGY_EVAL_RUBRIC:
        name = criterion["criterion"]
        weight = criterion["weight"]
        score = scores.get(name, 3)  # Default to 3 if missing

        total += score * weight
        total_weight += weight

    return round(total / total_weight if total_weight > 0 else 0, 2)
