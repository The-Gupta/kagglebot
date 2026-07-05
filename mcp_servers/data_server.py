"""
Data MCP Server — Exposes tools for dataset loading, profiling, and analysis.

Tools:
  - load_dataset(path): Loads CSV/Parquet files, returns shape and preview
  - compute_profile(path): Generates column-level statistics
  - analyze_target(path, target_col): Analyzes target variable distribution
  - detect_issues(path): Flags data quality issues

Each tool returns structured data that the Data Agent can reason about
and write to session state.
"""

import os
from typing import Any

import numpy as np
import pandas as pd


# Module-level cache for loaded dataframes (avoids re-reading files)
_dataframe_cache: dict[str, pd.DataFrame] = {}


def _get_dataframe(path: str) -> pd.DataFrame:
    """Loads and caches a dataframe from a file path."""
    if path in _dataframe_cache:
        return _dataframe_cache[path]

    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found: {path}")

    if path.endswith(".csv"):
        df = pd.read_csv(path)
    elif path.endswith(".parquet"):
        df = pd.read_parquet(path)
    elif path.endswith(".tsv"):
        df = pd.read_csv(path, sep="\t")
    else:
        raise ValueError(
            f"Unsupported file format: {path}. "
            "Supported: .csv, .parquet, .tsv"
        )

    _dataframe_cache[path] = df
    return df


def load_dataset(path: str) -> dict[str, Any]:
    """
    Loads a dataset file and returns basic information about it.

    Args:
        path: Path to the dataset file (CSV, Parquet, or TSV)

    Returns:
        Dictionary with:
        - shape: (rows, columns)
        - columns: List of column names with data types
        - preview: First 5 rows as a list of dicts
        - memory_usage: Approximate memory usage in MB
    """
    df = _get_dataframe(path)

    columns_info = []
    for col in df.columns:
        col_info = {
            "name": col,
            "dtype": str(df[col].dtype),
            "non_null_count": int(df[col].notna().sum()),
            "null_count": int(df[col].isna().sum()),
        }
        columns_info.append(col_info)

    # Convert preview to serializable format
    preview = df.head(5).fillna("NaN").to_dict(orient="records")

    return {
        "path": path,
        "shape": {"rows": df.shape[0], "columns": df.shape[1]},
        "columns": columns_info,
        "preview": preview,
        "memory_usage_mb": round(
            df.memory_usage(deep=True).sum() / (1024 * 1024), 2
        ),
    }


def compute_profile(path: str) -> dict[str, Any]:
    """
    Generates detailed column-level statistics for a dataset.

    Args:
        path: Path to the dataset file

    Returns:
        Dictionary with per-column statistics including:
        - Numeric columns: mean, std, min, max, median, quartiles
        - Categorical columns: unique count, top values, frequency
        - All columns: null percentage, data type
    """
    df = _get_dataframe(path)
    profile = {"columns": {}, "shape": {"rows": df.shape[0], "columns": df.shape[1]}}

    for col in df.columns:
        col_profile: dict[str, Any] = {
            "dtype": str(df[col].dtype),
            "null_count": int(df[col].isna().sum()),
            "null_percentage": round(
                df[col].isna().sum() / len(df) * 100, 1
            ),
            "unique_count": int(df[col].nunique()),
        }

        if pd.api.types.is_numeric_dtype(df[col]):
            # Numeric column statistics
            desc = df[col].describe()
            col_profile["type"] = "numeric"
            col_profile["mean"] = round(float(desc.get("mean", 0)), 4)
            col_profile["std"] = round(float(desc.get("std", 0)), 4)
            col_profile["min"] = round(float(desc.get("min", 0)), 4)
            col_profile["max"] = round(float(desc.get("max", 0)), 4)
            col_profile["median"] = round(float(df[col].median()), 4)
            col_profile["q25"] = round(float(desc.get("25%", 0)), 4)
            col_profile["q75"] = round(float(desc.get("75%", 0)), 4)

            # Check for potential ID column (all unique integers)
            if col_profile["unique_count"] == len(df) and df[col].dtype in [
                "int64",
                "int32",
            ]:
                col_profile["likely_id"] = True

            # Check skewness
            try:
                skew = float(df[col].skew())
                col_profile["skewness"] = round(skew, 4)
                if abs(skew) > 1:
                    col_profile["skewed"] = True
            except (TypeError, ValueError):
                pass

        else:
            # Categorical column statistics
            col_profile["type"] = "categorical"
            value_counts = df[col].value_counts()
            col_profile["top_values"] = {
                str(k): int(v) for k, v in value_counts.head(5).items()
            }
            col_profile["cardinality_ratio"] = round(
                col_profile["unique_count"] / len(df), 4
            )

            # Flag high cardinality (potential ID or free text)
            if col_profile["cardinality_ratio"] > 0.8:
                col_profile["high_cardinality"] = True

        profile["columns"][col] = col_profile

    return profile


def analyze_target(path: str, target_column: str) -> dict[str, Any]:
    """
    Analyzes the target variable to understand the prediction task.

    Args:
        path: Path to the dataset file
        target_column: Name of the target column

    Returns:
        Dictionary with:
        - task_type: 'binary_classification', 'multiclass_classification',
                     or 'regression'
        - distribution: Value counts or statistics
        - class_balance: For classification, the balance ratio
        - correlations: Top correlated features (for numeric targets)
    """
    df = _get_dataframe(path)

    if target_column not in df.columns:
        return {
            "error": f"Column '{target_column}' not found. "
            f"Available columns: {list(df.columns)}"
        }

    target = df[target_column]
    result: dict[str, Any] = {
        "column": target_column,
        "dtype": str(target.dtype),
        "null_count": int(target.isna().sum()),
    }

    unique_count = target.nunique()

    if unique_count <= 2:
        # Binary classification
        result["task_type"] = "binary_classification"
        value_counts = target.value_counts()
        result["distribution"] = {
            str(k): int(v) for k, v in value_counts.items()
        }
        majority = value_counts.iloc[0]
        minority = value_counts.iloc[1] if len(value_counts) > 1 else 0
        result["class_balance"] = {
            "majority_class": str(value_counts.index[0]),
            "majority_pct": round(majority / len(target) * 100, 1),
            "minority_class": (
                str(value_counts.index[1]) if len(value_counts) > 1 else "N/A"
            ),
            "minority_pct": round(minority / len(target) * 100, 1),
            "balance_ratio": round(minority / majority, 4) if majority > 0 else 0,
        }

    elif unique_count <= 20:
        # Multiclass classification
        result["task_type"] = "multiclass_classification"
        value_counts = target.value_counts()
        result["distribution"] = {
            str(k): int(v) for k, v in value_counts.items()
        }
        result["num_classes"] = unique_count

    else:
        # Regression
        result["task_type"] = "regression"
        result["distribution"] = {
            "mean": round(float(target.mean()), 4),
            "std": round(float(target.std()), 4),
            "min": round(float(target.min()), 4),
            "max": round(float(target.max()), 4),
            "median": round(float(target.median()), 4),
        }
        try:
            result["skewness"] = round(float(target.skew()), 4)
        except (TypeError, ValueError):
            pass

    # Compute correlations with numeric features
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if target_column in numeric_cols and len(numeric_cols) > 1:
        correlations = df[numeric_cols].corr()[target_column].drop(
            target_column, errors="ignore"
        )
        # Sort by absolute correlation
        correlations = correlations.abs().sort_values(ascending=False)
        result["top_correlations"] = {
            col: round(float(df[numeric_cols].corr()[target_column][col]), 4)
            for col in correlations.head(5).index
        }

    return result


def detect_issues(path: str) -> dict[str, Any]:
    """
    Detects data quality issues that could affect model performance.

    Args:
        path: Path to the dataset file

    Returns:
        Dictionary with detected issues:
        - high_null_columns: Columns with >30% null values
        - constant_columns: Columns with only one unique value
        - high_cardinality: Categorical columns with too many unique values
        - potential_leakage: Columns that might cause target leakage
        - duplicate_rows: Number of duplicate rows
        - potential_id_columns: Columns that look like IDs
        - overall_quality_score: 0-100 quality score
    """
    df = _get_dataframe(path)
    issues: dict[str, Any] = {
        "high_null_columns": [],
        "constant_columns": [],
        "high_cardinality_columns": [],
        "potential_id_columns": [],
        "duplicate_rows": 0,
        "warnings": [],
        "overall_quality_score": 100,
    }

    penalty = 0

    for col in df.columns:
        null_pct = df[col].isna().sum() / len(df) * 100

        # High null columns
        if null_pct > 30:
            issues["high_null_columns"].append(
                {"column": col, "null_pct": round(null_pct, 1)}
            )
            penalty += 5

        # Constant columns (useless for modeling)
        if df[col].nunique() <= 1:
            issues["constant_columns"].append(col)
            penalty += 3

        # High cardinality categorical columns
        if not pd.api.types.is_numeric_dtype(df[col]):
            cardinality_ratio = df[col].nunique() / len(df)
            if cardinality_ratio > 0.8:
                issues["high_cardinality_columns"].append(
                    {
                        "column": col,
                        "unique_values": int(df[col].nunique()),
                        "cardinality_ratio": round(cardinality_ratio, 4),
                    }
                )
                penalty += 2

        # Potential ID columns
        if (
            df[col].nunique() == len(df)
            and df[col].dtype in ["int64", "int32"]
        ):
            issues["potential_id_columns"].append(col)
            penalty += 1

    # Duplicate rows
    dup_count = int(df.duplicated().sum())
    issues["duplicate_rows"] = dup_count
    if dup_count > 0:
        issues["warnings"].append(
            f"Found {dup_count} duplicate rows "
            f"({round(dup_count/len(df)*100, 1)}% of data)"
        )
        penalty += 5

    # Small dataset warning
    if len(df) < 100:
        issues["warnings"].append(
            f"Small dataset ({len(df)} rows). "
            "Risk of overfitting. Use aggressive cross-validation."
        )
        penalty += 5
    elif len(df) < 1000:
        issues["warnings"].append(
            f"Moderately small dataset ({len(df)} rows). "
            "Consider using simpler models and strong regularization."
        )
        penalty += 2

    # Calculate quality score
    issues["overall_quality_score"] = max(0, 100 - penalty)

    # Generate actionable recommendations
    recommendations = []
    if issues["high_null_columns"]:
        recommendations.append(
            "Handle missing values: consider imputation (median/mode) "
            "or dropping columns with >50% nulls."
        )
    if issues["constant_columns"]:
        recommendations.append(
            f"Drop constant columns: {issues['constant_columns']}"
        )
    if issues["potential_id_columns"]:
        recommendations.append(
            f"Drop ID columns before training: {issues['potential_id_columns']}"
        )
    if issues["high_cardinality_columns"]:
        recommendations.append(
            "High cardinality categorical columns may need "
            "target encoding or frequency encoding."
        )

    issues["recommendations"] = recommendations

    return issues
