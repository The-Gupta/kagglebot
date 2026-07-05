"""
Data Profiler Skill — Reusable data profiling capability module.

This skill provides a high-level profiling function that orchestrates
multiple data analysis steps into a single comprehensive report.

Concept demonstrated: Agent Skills — Modular, reusable capability
that can be loaded by any agent that needs data analysis.
"""

from typing import Any

from mcp_servers.data_server import (
    analyze_target,
    compute_profile,
    detect_issues,
    load_dataset,
)


def generate_full_profile(
    path: str, target_column: str | None = None
) -> dict[str, Any]:
    """
    Generates a comprehensive data profile by combining all data tools.

    This is the primary skill function — it runs load, profile, target
    analysis, and issue detection in one call, producing a unified report.

    Args:
        path: Path to the dataset file
        target_column: Optional name of the target variable

    Returns:
        A comprehensive profile dictionary with all analysis results
        combined into a single structured report.
    """
    report: dict[str, Any] = {
        "dataset_path": path,
        "sections": {},
    }

    # Step 1: Load dataset basics
    try:
        load_result = load_dataset(path)
        report["sections"]["overview"] = load_result
    except Exception as e:
        report["sections"]["overview"] = {"error": str(e)}
        return report

    # Step 2: Compute detailed profile
    try:
        profile_result = compute_profile(path)
        report["sections"]["column_profiles"] = profile_result
    except Exception as e:
        report["sections"]["column_profiles"] = {"error": str(e)}

    # Step 3: Analyze target variable (if specified)
    if target_column:
        try:
            target_result = analyze_target(path, target_column)
            report["sections"]["target_analysis"] = target_result
        except Exception as e:
            report["sections"]["target_analysis"] = {"error": str(e)}

    # Step 4: Detect data quality issues
    try:
        issues_result = detect_issues(path)
        report["sections"]["quality_issues"] = issues_result
    except Exception as e:
        report["sections"]["quality_issues"] = {"error": str(e)}

    # Step 5: Generate summary
    overview = report["sections"].get("overview", {})
    issues = report["sections"].get("quality_issues", {})
    target = report["sections"].get("target_analysis", {})

    shape = overview.get("shape", {})
    report["summary"] = {
        "rows": shape.get("rows", 0),
        "columns": shape.get("columns", 0),
        "quality_score": issues.get("overall_quality_score", "N/A"),
        "task_type": target.get("task_type", "unknown"),
        "num_issues": (
            len(issues.get("high_null_columns", []))
            + len(issues.get("constant_columns", []))
            + len(issues.get("high_cardinality_columns", []))
        ),
        "recommendations": issues.get("recommendations", []),
    }

    return report


def format_profile_as_text(profile: dict[str, Any]) -> str:
    """
    Formats a profile report as human-readable text.

    Useful for displaying in chat or writing to files.
    """
    lines = []
    summary = profile.get("summary", {})

    lines.append("=" * 60)
    lines.append("  📊 DATA PROFILE REPORT")
    lines.append("=" * 60)
    lines.append("")

    # Overview
    lines.append(f"  Dataset: {profile.get('dataset_path', 'unknown')}")
    lines.append(
        f"  Shape: {summary.get('rows', '?')} rows × "
        f"{summary.get('columns', '?')} columns"
    )
    lines.append(f"  Quality Score: {summary.get('quality_score', '?')}/100")
    lines.append(f"  Task Type: {summary.get('task_type', 'unknown')}")
    lines.append("")

    # Issues
    num_issues = summary.get("num_issues", 0)
    if num_issues > 0:
        lines.append(f"  ⚠️  {num_issues} issue(s) detected:")
        for rec in summary.get("recommendations", []):
            lines.append(f"    • {rec}")
        lines.append("")

    # Target analysis
    target = profile.get("sections", {}).get("target_analysis", {})
    if target and "task_type" in target:
        lines.append("  🎯 Target Variable:")
        lines.append(f"    Column: {target.get('column', '?')}")
        lines.append(f"    Task: {target.get('task_type', '?')}")
        if "class_balance" in target:
            balance = target["class_balance"]
            lines.append(
                f"    Balance: {balance.get('majority_pct', '?')}% / "
                f"{balance.get('minority_pct', '?')}%"
            )
        if "top_correlations" in target:
            lines.append("    Top correlations:")
            for col, corr in list(target["top_correlations"].items())[:3]:
                lines.append(f"      {col}: {corr}")
        lines.append("")

    lines.append("=" * 60)

    return "\n".join(lines)
