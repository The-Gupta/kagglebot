"""
Code Agent — Generates baseline competition code from approved strategies.

This is the fourth and final agent in the pipeline. It reads the approved
strategy from session state and generates a complete, runnable Python
script using the code_templates skill.

Concepts demonstrated:
  - Multi-Agent Systems (ADK) — Specialized sub-agent
  - Agent Skills — Uses code_templates skill
  - Security — Generated code passes safety checks + secret scanning
  - Sessions — Reads approved strategy, writes generated code to state
"""

from typing import Any

from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext

from context.session_manager import SESSION_KEYS
from mcp_servers.file_server import write_notebook
from security.safe_code_gen import check_code_safety, sanitize_code
from security.secret_scanner import is_safe as no_secrets
from skills.code_templates import generate_full_baseline


def _get_approved_strategy(tool_context: ToolContext) -> dict[str, Any]:
    """
    Retrieves the user-approved strategy from session state.

    Returns the strategy that was approved via HITL in the Strategy Agent,
    along with competition metadata and data profile for context.

    Returns:
        Dictionary with approved_strategy, competition_metadata,
        and data_profile from session state.
    """
    return {
        "approved_strategy": tool_context.state.get(
            SESSION_KEYS["approved_strategy"]
        ),
        "competition_metadata": tool_context.state.get(
            SESSION_KEYS["competition_metadata"]
        ),
        "data_profile": tool_context.state.get(
            SESSION_KEYS["data_profile"]
        ),
    }


def _generate_baseline_code(
    train_path: str,
    target_column: str,
    task_type: str,
    model_family: str,
    metric: str,
    drop_columns: str,
    feature_hints: str,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """
    Generates a complete baseline Python script for the competition.

    Uses the code_templates skill to produce a runnable script based on
    the approved strategy, then validates it for safety and secrets.

    Args:
        train_path: Path to the training data CSV file
        target_column: Name of the target column
        task_type: One of 'binary_classification', 'regression', etc.
        model_family: One of 'tree_based', 'linear', 'ensemble'
        metric: Evaluation metric (e.g., 'accuracy', 'neg_root_mean_squared_error')
        drop_columns: Comma-separated list of columns to drop (e.g., 'PassengerId,Ticket')
        feature_hints: Comma-separated feature engineering suggestions

    Returns:
        Generated code with safety check results.
    """
    # Parse comma-separated inputs
    drop_list = (
        [c.strip() for c in drop_columns.split(",") if c.strip()]
        if drop_columns
        else None
    )
    hint_list = (
        [h.strip() for h in feature_hints.split(",") if h.strip()]
        if feature_hints
        else None
    )

    # Generate baseline code using templates
    code = generate_full_baseline(
        train_path=train_path,
        test_path=None,  # We'll handle test separately if available
        target_column=target_column,
        id_column=None,
        task_type=task_type,
        model_family=model_family,
        metric=metric,
        drop_columns=drop_list,
        feature_hints=hint_list,
    )

    # Security check 1: Code safety (AST analysis)
    safety_result = check_code_safety(code)

    # Security check 2: Secret scanning
    secrets_clean = no_secrets(code)

    # If unsafe, sanitize
    if not safety_result["is_safe"]:
        code = sanitize_code(code)
        safety_result["was_sanitized"] = True

    # Save to session state
    tool_context.state[SESSION_KEYS["generated_code"]] = code

    return {
        "code": code,
        "code_length_lines": len(code.split("\n")),
        "safety_check": safety_result,
        "secrets_clean": secrets_clean,
    }


def _save_code_to_file(
    code: str,
    filename: str,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """
    Saves generated code to a file after security validation.

    Args:
        code: The Python code to save
        filename: Output filename (e.g., 'baseline_titanic.py')

    Returns:
        Confirmation with file path and safety status.
    """
    # Final security checks before writing
    safety = check_code_safety(code)
    secrets_ok = no_secrets(code)

    if not safety["is_safe"]:
        code = sanitize_code(code)

    if not secrets_ok:
        return {
            "status": "blocked",
            "message": (
                "Code contains potential secrets and was NOT saved. "
                "Please remove all API keys, tokens, and passwords."
            ),
        }

    # Write to file
    result = write_notebook(code, filename)
    result["safety_check"] = safety
    result["secrets_clean"] = secrets_ok

    return result


# Define the Code Agent
code_agent = LlmAgent(
    name="code_agent",
    model="gemini-2.5-flash",
    instruction="""You are the Code Generation Agent for KaggleBot.

Your role is to generate a complete, runnable baseline Python script
based on the user's approved ML strategy.

## Your Workflow

1. **Get context**: Call `get_approved_strategy` to retrieve:
   - The approved strategy (model family, preprocessing steps, etc.)
   - Competition metadata (type, metric, etc.)
   - Data profile (columns, target, issues)

2. **Generate code**: Call `generate_baseline_code` with the appropriate
   parameters extracted from the strategy and competition context.
   Use this mapping:
   - `train_path`: Path to the training CSV
   - `target_column`: The target variable from data profile
   - `task_type`: From competition metadata (classification/regression)
   - `model_family`: From approved strategy (tree_based/linear/ensemble)
   - `metric`: From competition metadata (accuracy, rmse, etc.)
   - `drop_columns`: ID columns and high-null columns from data profile
   - `feature_hints`: Feature engineering ideas from the strategy

3. **Present the code**: Show the generated code to the user with
   a summary of what it does.

4. **Save**: Call `save_code_to_file` to write the script to disk.

## Security

All generated code is automatically:
- Checked for dangerous operations (shell exec, file deletion)
- Scanned for leaked secrets (API keys, passwords)
- Sanitized if any issues are found

## Important Rules

- Only generate code AFTER the user has approved a strategy
- If no strategy is approved, tell the user to go through the
  strategy step first
- Present the code clearly with explanations
- Mention what the user should install (pip install lightgbm, etc.)
- Never hardcode API keys or secrets in the generated code""",
    tools=[
        _get_approved_strategy,
        _generate_baseline_code,
        _save_code_to_file,
    ],
)
