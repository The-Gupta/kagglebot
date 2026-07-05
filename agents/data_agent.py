"""
Data Agent — Dataset profiler that analyzes competition data.

This is the second agent in the pipeline. It reads the competition
metadata from session state (written by Scraper Agent), profiles the
dataset, and writes a data profile report to session state.

Concepts demonstrated:
  - Multi-Agent Systems (ADK) — Specialized sub-agent
  - Agent Skills — Uses the data_profiler skill
  - Sessions — Reads from Scraper Agent's state, writes its own
"""

import os
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext

from context.session_manager import SESSION_KEYS
from mcp_servers.data_server import (
    analyze_target,
    compute_profile,
    detect_issues,
    load_dataset,
)


def _load_and_preview(path: str, tool_context: ToolContext) -> dict[str, Any]:
    """
    Loads a dataset and returns basic information.

    Args:
        path: Path to the dataset file (CSV, Parquet, or TSV)

    Returns:
        Dataset shape, column info, and preview rows.
    """
    result = load_dataset(path)

    # Store the path in session state so other tools can access it
    tool_context.state["dataset_path"] = path

    return result


def _profile_dataset(path: str, tool_context: ToolContext) -> dict[str, Any]:
    """
    Generates detailed column-level statistics for the dataset.

    Args:
        path: Path to the dataset file

    Returns:
        Per-column statistics including types, distributions, and outliers.
    """
    return compute_profile(path)


def _analyze_target_variable(
    path: str, target_column: str, tool_context: ToolContext
) -> dict[str, Any]:
    """
    Analyzes the target variable to understand the prediction task.

    Args:
        path: Path to the dataset file
        target_column: Name of the target column to analyze

    Returns:
        Task type (classification/regression), distribution, and correlations.
    """
    return analyze_target(path, target_column)


def _check_data_quality(
    path: str, tool_context: ToolContext
) -> dict[str, Any]:
    """
    Detects data quality issues that could affect model performance.

    Args:
        path: Path to the dataset file

    Returns:
        List of issues: high nulls, constant columns, duplicates, etc.
    """
    return detect_issues(path)


def _save_profile_to_session(
    profile_summary: str, tool_context: ToolContext
) -> dict[str, str]:
    """
    Saves the data profile summary to session state for downstream agents.

    Call this AFTER you have completed your analysis. Pass a comprehensive
    text summary of your findings as the profile_summary.

    Args:
        profile_summary: A comprehensive text summary of the data profile
            including shape, key features, issues, target analysis, and
            recommendations. This will be used by the Strategy Agent.

    Returns:
        Confirmation that the profile was saved.
    """
    tool_context.state[SESSION_KEYS["data_profile"]] = profile_summary

    return {
        "status": "saved",
        "message": "Data profile saved to session state. "
        "The Strategy Agent can now use this information.",
    }


# Resolve sample data path relative to project root
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SAMPLE_DATA_DIR = os.path.join(_PROJECT_ROOT, "data")


# Define the Data Agent
data_agent = LlmAgent(
    name="data_agent",
    model="gemini-2.5-flash",
    instruction=f"""You are the Data Analysis Agent for KaggleBot.

Your role is to profile a dataset and produce a comprehensive analysis
that the Strategy Agent can use to recommend ML approaches.

## Available Sample Datasets
The following sample datasets are available for analysis:
- `{_SAMPLE_DATA_DIR}/titanic_train.csv` — Titanic training data

## Your Workflow

When asked to analyze a dataset:

1. **Load the dataset** using `load_and_preview` to see shape and columns
2. **Profile all columns** using `profile_dataset` for detailed statistics
3. **Analyze the target** using `analyze_target_variable` to understand
   the prediction task (classification vs regression, class balance, etc.)
4. **Check data quality** using `check_data_quality` to find issues
5. **Save your findings** using `save_profile_to_session` with a
   comprehensive text summary

## Using Competition Metadata

Check the session state for competition metadata from the Scraper Agent.
If available, use it to:
- Identify the correct target column
- Understand the evaluation metric
- Focus your analysis on relevant features

## Your Report MUST Include

- 📊 **Shape**: rows × columns
- 📋 **Column Overview**: key columns, types, null counts
- 🎯 **Target Variable**: task type, distribution, class balance
- ⚠️ **Data Quality Issues**: missing values, high cardinality, duplicates
- 💡 **Feature Engineering Hints**: columns that could be transformed
- 📈 **Top Correlations**: features most correlated with the target

Be thorough but concise. Your analysis directly feeds the Strategy Agent.

IMPORTANT: After completing your analysis, you MUST call
`save_profile_to_session` with your full summary text. Without this,
the Strategy Agent won't have access to your findings.""",
    tools=[
        _load_and_preview,
        _profile_dataset,
        _analyze_target_variable,
        _check_data_quality,
        _save_profile_to_session,
    ],
)
