"""
File MCP Server — Exposes tools for writing reports and notebooks.

Tools:
  - write_report(content, path): Writes markdown content to a file
  - write_notebook(code, path): Writes Python code to a file

These tools allow agents to produce persistent output files
that the user can review, modify, and use.
"""

import os
from typing import Any


# Default output directory
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(_PROJECT_ROOT, "output")


def _ensure_output_dir(path: str) -> str:
    """Ensures the directory for the output file exists."""
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    return path


def write_report(content: str, filename: str = "strategy_report.md") -> dict[str, Any]:
    """
    Writes a markdown report to the output directory.

    Args:
        content: The markdown content to write
        filename: Output filename (default: strategy_report.md)

    Returns:
        Confirmation with the file path.
    """
    path = os.path.join(OUTPUT_DIR, filename)
    _ensure_output_dir(path)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return {
        "status": "success",
        "path": path,
        "size_bytes": os.path.getsize(path),
        "message": f"Report written to {path}",
    }


def write_notebook(
    code: str, filename: str = "baseline_notebook.py"
) -> dict[str, Any]:
    """
    Writes Python code to a file in the output directory.

    Args:
        code: The Python code to write
        filename: Output filename (default: baseline_notebook.py)

    Returns:
        Confirmation with the file path.
    """
    path = os.path.join(OUTPUT_DIR, filename)
    _ensure_output_dir(path)

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    return {
        "status": "success",
        "path": path,
        "size_bytes": os.path.getsize(path),
        "message": f"Notebook written to {path}",
    }
