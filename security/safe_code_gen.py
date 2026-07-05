"""
Safe Code Generation — Guardrails for auto-generated Python code.

Validates generated code before writing to disk. Prevents dangerous
operations like arbitrary file deletion, network requests to unknown
hosts, or execution of shell commands.

Concept demonstrated: Security Features — Sandboxing constraints
on agent-generated code.
"""

import ast
import re
from typing import Any


# Dangerous function calls that should not appear in generated code
BLOCKED_CALLS = {
    "os.system",
    "os.popen",
    "os.exec",
    "os.execl",
    "os.execle",
    "os.execlp",
    "os.execv",
    "os.execve",
    "os.execvp",
    "os.execvpe",
    "subprocess.call",
    "subprocess.run",
    "subprocess.Popen",
    "subprocess.check_call",
    "subprocess.check_output",
    "eval",
    "exec",
    "compile",
    "__import__",
    "shutil.rmtree",
    "os.remove",
    "os.rmdir",
    "os.unlink",
}

# Dangerous imports
BLOCKED_IMPORTS = {
    "subprocess",
    "shutil",
    "socket",
    "http.server",
    "ftplib",
    "telnetlib",
    "ctypes",
    "pickle",  # Deserialization attacks
}

# Allowed imports for ML code
ALLOWED_IMPORTS = {
    "pandas", "numpy", "sklearn", "lightgbm", "xgboost", "catboost",
    "scipy", "matplotlib", "seaborn", "plotly",
    "os",  # For os.path operations only
    "warnings", "json", "csv", "re", "math",
    "collections", "itertools", "functools",
    "typing", "datetime", "pathlib",
}


def check_code_safety(code: str) -> dict[str, Any]:
    """
    Analyzes generated Python code for safety issues.

    Uses AST parsing to detect dangerous operations without executing code.

    Args:
        code: The Python code to check

    Returns:
        Dictionary with:
        - is_safe: bool — whether the code passes all checks
        - issues: list — detected safety issues
        - warnings: list — non-blocking concerns
    """
    result: dict[str, Any] = {
        "is_safe": True,
        "issues": [],
        "warnings": [],
    }

    # Try to parse the code
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        result["issues"].append(
            f"Syntax error in generated code at line {e.lineno}: {e.msg}"
        )
        result["is_safe"] = False
        return result

    # Walk the AST to check for dangerous patterns
    for node in ast.walk(tree):
        # Check function calls
        if isinstance(node, ast.Call):
            call_name = _get_call_name(node)
            if call_name and call_name in BLOCKED_CALLS:
                result["issues"].append(
                    f"Blocked function call: '{call_name}' "
                    f"(line {node.lineno})"
                )
                result["is_safe"] = False

        # Check imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name.split(".")[0]
                if module in BLOCKED_IMPORTS:
                    result["issues"].append(
                        f"Blocked import: '{alias.name}' (line {node.lineno})"
                    )
                    result["is_safe"] = False
                elif module not in ALLOWED_IMPORTS:
                    result["warnings"].append(
                        f"Uncommon import: '{alias.name}' (line {node.lineno})"
                    )

        if isinstance(node, ast.ImportFrom):
            if node.module:
                module = node.module.split(".")[0]
                if module in BLOCKED_IMPORTS:
                    result["issues"].append(
                        f"Blocked import: 'from {node.module}' "
                        f"(line {node.lineno})"
                    )
                    result["is_safe"] = False

    # Regex-based checks for patterns that AST might miss
    dangerous_patterns = [
        (r"open\s*\([^)]*,\s*['\"]w['\"]", "File write operation"),
        (r"requests\.(?:get|post|put|delete)\s*\(", "HTTP request"),
        (r"urllib\.request", "HTTP request via urllib"),
    ]

    for pattern, description in dangerous_patterns:
        matches = list(re.finditer(pattern, code))
        for match in matches:
            line_num = code[:match.start()].count("\n") + 1
            # Allow pandas to_csv (it uses file writing but is safe)
            line = code.split("\n")[line_num - 1]
            if "to_csv" in line or "to_parquet" in line:
                continue
            result["warnings"].append(
                f"{description} at line {line_num}"
            )

    return result


def _get_call_name(node: ast.Call) -> str | None:
    """Extracts the full function name from a Call AST node."""
    if isinstance(node.func, ast.Name):
        return node.func.id
    elif isinstance(node.func, ast.Attribute):
        parts = []
        current = node.func
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return ".".join(reversed(parts))
    return None


def sanitize_code(code: str) -> str:
    """
    Removes or comments out dangerous code patterns.

    Args:
        code: The Python code to sanitize

    Returns:
        Sanitized code with dangerous patterns commented out
    """
    lines = code.split("\n")
    sanitized = []

    for line in lines:
        stripped = line.strip()

        # Comment out dangerous imports
        for blocked in BLOCKED_IMPORTS:
            if re.match(
                rf"(?:import\s+{blocked}|from\s+{blocked})", stripped
            ):
                line = f"# [BLOCKED] {line}"
                break

        # Comment out dangerous function calls
        for blocked_call in BLOCKED_CALLS:
            if blocked_call in stripped:
                line = f"# [BLOCKED] {line}"
                break

        sanitized.append(line)

    return "\n".join(sanitized)
