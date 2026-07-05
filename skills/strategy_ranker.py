"""
Strategy Ranker Skill — Reusable ML strategy ranking capability.

Provides template-based strategy generation for common competition types.
The Strategy Agent uses this skill to generate initial strategy candidates,
then applies LLM reasoning to rank and customize them.

Concept demonstrated: Agent Skills — Modular, reusable capability
that encapsulates domain knowledge about ML competition strategies.
"""

from typing import Any


# Strategy templates organized by competition type
STRATEGY_TEMPLATES: dict[str, list[dict[str, Any]]] = {
    "binary_classification": [
        {
            "name": "Gradient Boosting Baseline",
            "model_family": "tree_based",
            "models": ["LightGBM", "XGBoost", "CatBoost"],
            "description": (
                "Tree-based gradient boosting models are the default "
                "choice for tabular binary classification. They handle "
                "mixed feature types, missing values, and nonlinear "
                "relationships well with minimal preprocessing."
            ),
            "preprocessing": [
                "Drop ID columns",
                "Handle missing values (median for numeric, mode for categorical)",
                "Label encode categorical features (or use native categorical support)",
                "No need for feature scaling",
            ],
            "feature_engineering": [
                "Create interaction features for top correlated columns",
                "Bin continuous variables (Age, Fare) into categories",
                "Extract information from text fields (e.g., titles from names)",
                "Create aggregate features (family size, is_alone)",
            ],
            "validation": "5-fold Stratified K-Fold cross-validation",
            "expected_score_range": "0.75 - 0.82",
            "effort": "Medium",
            "risk": "Low",
        },
        {
            "name": "Stacked Ensemble",
            "model_family": "ensemble",
            "models": [
                "LightGBM + XGBoost + RandomForest + LogisticRegression"
            ],
            "description": (
                "Stacking multiple diverse models often pushes accuracy "
                "2-5% beyond single model approaches. Use diverse base "
                "learners (trees, linear, KNN) with a simple meta-learner."
            ),
            "preprocessing": [
                "Same as Gradient Boosting Baseline",
                "Additional: create standardized features for linear models",
            ],
            "feature_engineering": [
                "Same as Gradient Boosting Baseline",
                "Additional: polynomial features for linear meta-learner",
            ],
            "validation": "Nested cross-validation (5-fold outer, 3-fold inner)",
            "expected_score_range": "0.78 - 0.85",
            "effort": "High",
            "risk": "Medium",
        },
        {
            "name": "Logistic Regression Baseline",
            "model_family": "linear",
            "models": ["LogisticRegression"],
            "description": (
                "Simple, interpretable baseline. Useful for understanding "
                "feature importance and as a benchmark for more complex "
                "models. Often surprisingly competitive on small datasets."
            ),
            "preprocessing": [
                "Drop ID columns",
                "Impute missing values",
                "One-hot encode categorical features",
                "Standard scale numeric features",
            ],
            "feature_engineering": [
                "Create polynomial features (degree 2) for top features",
                "Bin continuous variables",
            ],
            "validation": "5-fold Stratified K-Fold",
            "expected_score_range": "0.72 - 0.78",
            "effort": "Low",
            "risk": "Low",
        },
    ],
    "regression": [
        {
            "name": "Gradient Boosting Regression",
            "model_family": "tree_based",
            "models": ["LightGBM", "XGBoost", "CatBoost"],
            "description": (
                "Gradient boosting is the go-to for tabular regression. "
                "Use RMSLE-aware loss if that's the metric. Consider "
                "log-transforming the target for right-skewed distributions."
            ),
            "preprocessing": [
                "Drop ID columns",
                "Handle missing values",
                "Log-transform skewed target variables",
                "Label encode categorical features",
            ],
            "feature_engineering": [
                "Create aggregate features (total area, total quality)",
                "Extract temporal features from dates",
                "Create ratio features",
                "Remove outliers carefully",
            ],
            "validation": "5-fold K-Fold cross-validation",
            "expected_score_range": "Depends on metric",
            "effort": "Medium",
            "risk": "Low",
        },
        {
            "name": "Stacked Ensemble Regression",
            "model_family": "ensemble",
            "models": ["LightGBM + Ridge + ElasticNet + SVR"],
            "description": (
                "Combine diverse regressors for better generalization. "
                "Use a Ridge or linear meta-learner on top of tree-based "
                "and linear base models."
            ),
            "preprocessing": [
                "Same as Gradient Boosting Regression",
                "Standardize features for linear models",
            ],
            "feature_engineering": [
                "Same as Gradient Boosting Regression",
                "Polynomial features for linear models",
            ],
            "validation": "Nested cross-validation",
            "expected_score_range": "Usually 5-10% better than single model",
            "effort": "High",
            "risk": "Medium",
        },
    ],
    "multiclass_classification": [
        {
            "name": "Gradient Boosting Multiclass",
            "model_family": "tree_based",
            "models": ["LightGBM", "XGBoost"],
            "description": (
                "Gradient boosting with softmax/multiclass objective. "
                "Handles multiple classes natively."
            ),
            "preprocessing": [
                "Drop ID columns",
                "Handle missing values",
                "Label encode categorical features",
            ],
            "feature_engineering": [
                "Create class-specific features",
                "Use target encoding with cross-validation",
            ],
            "validation": "5-fold Stratified K-Fold",
            "expected_score_range": "Depends on number of classes",
            "effort": "Medium",
            "risk": "Low",
        },
    ],
}

# Fallback for unknown competition types
DEFAULT_STRATEGIES = STRATEGY_TEMPLATES["binary_classification"]


def get_strategies_for_type(
    competition_type: str,
) -> list[dict[str, Any]]:
    """
    Returns strategy templates appropriate for the competition type.

    Args:
        competition_type: One of 'binary_classification', 'regression',
            'multiclass_classification', 'nlp', 'computer_vision', 'unknown'

    Returns:
        List of strategy template dictionaries.
    """
    # Map common types to our template keys
    type_mapping = {
        "classification": "binary_classification",
        "binary_classification": "binary_classification",
        "multiclass_classification": "multiclass_classification",
        "regression": "regression",
    }

    mapped_type = type_mapping.get(competition_type, competition_type)
    return STRATEGY_TEMPLATES.get(mapped_type, DEFAULT_STRATEGIES)


def rank_strategies(
    strategies: list[dict[str, Any]],
    dataset_size: int = 0,
    num_features: int = 0,
) -> list[dict[str, Any]]:
    """
    Ranks strategies based on dataset characteristics.

    Applies heuristics to adjust rankings based on dataset size,
    feature count, and other properties.

    Args:
        strategies: List of strategy templates
        dataset_size: Number of rows in the training set
        num_features: Number of features

    Returns:
        Strategies sorted by recommended order with rank added.
    """
    ranked = []

    for strategy in strategies:
        score = 50  # Base score

        # Prefer simpler models for small datasets
        if dataset_size < 500:
            if strategy["model_family"] == "linear":
                score += 20  # Simpler models for small data
            elif strategy["model_family"] == "ensemble":
                score -= 10  # Ensembles overfit on small data
        elif dataset_size > 10000:
            if strategy["model_family"] == "tree_based":
                score += 15  # Trees shine on larger data
            if strategy["model_family"] == "ensemble":
                score += 10  # Ensembles worth the complexity

        # Effort/risk weighting
        effort_scores = {"Low": 10, "Medium": 5, "High": 0}
        risk_scores = {"Low": 10, "Medium": 5, "High": 0}
        score += effort_scores.get(strategy.get("effort", "Medium"), 5)
        score += risk_scores.get(strategy.get("risk", "Medium"), 5)

        strategy_copy = dict(strategy)
        strategy_copy["ranking_score"] = score
        ranked.append(strategy_copy)

    # Sort by score descending
    ranked.sort(key=lambda x: x["ranking_score"], reverse=True)

    # Add rank numbers
    for i, strategy in enumerate(ranked):
        strategy["rank"] = i + 1

    return ranked


def format_strategies_as_text(strategies: list[dict[str, Any]]) -> str:
    """Formats ranked strategies as human-readable text."""
    lines = []

    for s in strategies:
        lines.append(f"### Strategy #{s.get('rank', '?')}: {s['name']}")
        lines.append(f"**Models**: {', '.join(s.get('models', []))}")
        lines.append(f"**Description**: {s.get('description', '')}")
        lines.append(
            f"**Expected Score**: {s.get('expected_score_range', 'N/A')}"
        )
        lines.append(
            f"**Effort**: {s.get('effort', 'N/A')} | "
            f"**Risk**: {s.get('risk', 'N/A')}"
        )
        lines.append("")
        lines.append("**Preprocessing**:")
        for step in s.get("preprocessing", []):
            lines.append(f"  - {step}")
        lines.append("")
        lines.append("**Feature Engineering**:")
        for step in s.get("feature_engineering", []):
            lines.append(f"  - {step}")
        lines.append("")
        lines.append(f"**Validation**: {s.get('validation', 'N/A')}")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)
