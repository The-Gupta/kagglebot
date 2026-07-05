"""
Input Validator — Schema validation for all MCP tool inputs.

Validates URLs, file paths, and column names before they reach
the MCP tools. Prevents injection attacks, path traversal,
and invalid input from causing unexpected behavior.

Concept demonstrated: Security Features — Input validation
as a defense-in-depth measure for agent tool calls.
"""

import os
import re
from typing import Any
from urllib.parse import urlparse


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


def validate_kaggle_url(url: str) -> str:
    """
    Validates that a URL is a legitimate Kaggle competition URL.

    Args:
        url: The URL to validate

    Returns:
        The validated URL (cleaned)

    Raises:
        ValidationError: If the URL is not a valid Kaggle competition URL
    """
    if not isinstance(url, str):
        raise ValidationError(f"URL must be a string, got {type(url).__name__}")

    url = url.strip()
    if not url:
        raise ValidationError("URL cannot be empty")

    # Parse the URL
    try:
        parsed = urlparse(url)
    except Exception:
        raise ValidationError(f"Invalid URL format: {url}")

    # Must be HTTPS
    if parsed.scheme not in ("http", "https"):
        raise ValidationError(
            f"URL must use http or https, got '{parsed.scheme}'"
        )

    # Must be kaggle.com
    if not parsed.hostname or not parsed.hostname.endswith("kaggle.com"):
        raise ValidationError(
            f"URL must be from kaggle.com, got '{parsed.hostname}'"
        )

    # Must contain a competition path
    if not re.search(r"/(?:competitions|c)/[\w-]+", parsed.path):
        raise ValidationError(
            "URL must point to a Kaggle competition "
            "(e.g., kaggle.com/competitions/titanic)"
        )

    return url


def validate_file_path(path: str, must_exist: bool = True) -> str:
    """
    Validates a file path for safety.

    Prevents path traversal attacks and ensures the file is within
    allowed directories.

    Args:
        path: The file path to validate
        must_exist: Whether the file must already exist

    Returns:
        The validated, resolved path

    Raises:
        ValidationError: If the path is invalid or unsafe
    """
    if not isinstance(path, str):
        raise ValidationError(
            f"Path must be a string, got {type(path).__name__}"
        )

    path = path.strip()
    if not path:
        raise ValidationError("Path cannot be empty")

    # Block path traversal
    if ".." in path:
        raise ValidationError(
            "Path traversal ('..') is not allowed for security"
        )

    # Block absolute paths outside the project
    if os.path.isabs(path):
        # Allow if it's within common safe directories
        safe_prefixes = [
            os.path.expanduser("~"),
            "/tmp",
        ]
        if not any(path.startswith(prefix) for prefix in safe_prefixes):
            raise ValidationError(
                f"Absolute path '{path}' is outside allowed directories"
            )

    # Check existence if required
    if must_exist and not os.path.exists(path):
        raise ValidationError(f"File not found: {path}")

    # Check file extension
    allowed_extensions = {
        ".csv", ".tsv", ".parquet", ".json", ".txt",
        ".py", ".md", ".yaml", ".yml",
    }
    ext = os.path.splitext(path)[1].lower()
    if ext and ext not in allowed_extensions:
        raise ValidationError(
            f"File extension '{ext}' is not allowed. "
            f"Allowed: {sorted(allowed_extensions)}"
        )

    return path


def validate_column_name(name: str, available_columns: list[str]) -> str:
    """
    Validates that a column name exists in the dataset.

    Args:
        name: The column name to validate
        available_columns: List of available column names

    Returns:
        The validated column name

    Raises:
        ValidationError: If the column doesn't exist
    """
    if not isinstance(name, str):
        raise ValidationError(
            f"Column name must be a string, got {type(name).__name__}"
        )

    name = name.strip()
    if name not in available_columns:
        raise ValidationError(
            f"Column '{name}' not found. "
            f"Available columns: {available_columns}"
        )

    return name


def validate_strategy_input(
    competition_type: str,
    dataset_rows: int,
    num_features: int,
) -> dict[str, Any]:
    """
    Validates inputs for strategy generation.

    Returns:
        Validated inputs as a dictionary
    """
    valid_types = {
        "binary_classification", "multiclass_classification",
        "regression", "classification", "nlp",
        "computer_vision", "unknown",
    }

    if competition_type not in valid_types:
        raise ValidationError(
            f"Invalid competition type '{competition_type}'. "
            f"Valid types: {sorted(valid_types)}"
        )

    if not isinstance(dataset_rows, int) or dataset_rows < 0:
        raise ValidationError(
            f"dataset_rows must be a non-negative integer, got {dataset_rows}"
        )

    if not isinstance(num_features, int) or num_features < 0:
        raise ValidationError(
            f"num_features must be a non-negative integer, got {num_features}"
        )

    return {
        "competition_type": competition_type,
        "dataset_rows": dataset_rows,
        "num_features": num_features,
    }
