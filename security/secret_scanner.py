"""
Secret Scanner — Ensures no API keys or secrets leak into generated code.

Scans generated code and output files for patterns that look like
API keys, tokens, passwords, or other secrets. Blocks output that
contains potential secrets.

Concept demonstrated: Security Features — Preventing accidental
secret exposure in auto-generated code.
"""

import re
from typing import Any


# Patterns that indicate potential secrets
SECRET_PATTERNS = [
    # API keys (common formats)
    (r"(?:api[_-]?key|apikey)\s*[=:]\s*['\"][A-Za-z0-9_\-]{20,}['\"]",
     "API key assignment"),
    (r"AIza[0-9A-Za-z_\-]{35}",
     "Google API key"),
    (r"sk-[A-Za-z0-9]{20,}",
     "OpenAI/Stripe secret key"),
    (r"ghp_[A-Za-z0-9]{36}",
     "GitHub personal access token"),

    # AWS
    (r"AKIA[0-9A-Z]{16}",
     "AWS access key"),
    (r"(?:aws[_-]?secret|secret[_-]?key)\s*[=:]\s*['\"][A-Za-z0-9/+=]{40}['\"]",
     "AWS secret key"),

    # Generic secrets
    (r"(?:password|passwd|pwd)\s*[=:]\s*['\"][^'\"]{8,}['\"]",
     "Password assignment"),
    (r"(?:secret|token)\s*[=:]\s*['\"][A-Za-z0-9_\-]{16,}['\"]",
     "Secret/token assignment"),

    # Bearer tokens
    (r"Bearer\s+[A-Za-z0-9_\-\.]{20,}",
     "Bearer token"),

    # Private keys
    (r"-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----",
     "Private key"),

    # Connection strings
    (r"(?:mongodb|postgres|mysql|redis)://[^\s]{20,}",
     "Database connection string"),
]

# Patterns to exclude (false positives)
SAFE_PATTERNS = [
    r"your_[a-z_]+_here",  # Placeholder values
    r"example\.com",
    r"localhost",
    r"API_KEY\s*=\s*os\.(?:getenv|environ)",  # Reading from env (safe)
    r"\.env",  # Reference to .env file
]


def scan_for_secrets(content: str) -> list[dict[str, Any]]:
    """
    Scans text content for potential secrets.

    Args:
        content: The text content to scan (code, config, etc.)

    Returns:
        List of findings, each with:
        - pattern_name: What was detected
        - line_number: Where it was found
        - line_content: The offending line (truncated)
        - severity: 'high' or 'medium'
    """
    findings = []

    # Check each line
    for line_num, line in enumerate(content.split("\n"), start=1):
        # Skip comments
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("//"):
            continue

        # Check against each secret pattern
        for pattern, name in SECRET_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                # Check if it's a known safe pattern (false positive)
                is_safe = any(
                    re.search(safe_pat, line, re.IGNORECASE)
                    for safe_pat in SAFE_PATTERNS
                )

                if not is_safe:
                    # Truncate the line for safety
                    truncated = line[:80] + "..." if len(line) > 80 else line
                    findings.append({
                        "pattern_name": name,
                        "line_number": line_num,
                        "line_content": truncated.strip(),
                        "severity": "high",
                    })

    return findings


def is_safe(content: str) -> bool:
    """
    Quick check: returns True if no secrets are found.

    Args:
        content: The text content to check

    Returns:
        True if safe (no secrets found), False otherwise
    """
    return len(scan_for_secrets(content)) == 0


def redact_secrets(content: str) -> str:
    """
    Replaces detected secrets with placeholder values.

    Args:
        content: The text content to redact

    Returns:
        Content with secrets replaced by [REDACTED]
    """
    redacted = content

    for pattern, name in SECRET_PATTERNS:
        # Check if any match is NOT a safe pattern before redacting
        for match in re.finditer(pattern, redacted, re.IGNORECASE):
            match_text = match.group()
            is_safe_match = any(
                re.search(safe_pat, match_text, re.IGNORECASE)
                for safe_pat in SAFE_PATTERNS
            )
            if not is_safe_match:
                redacted = redacted.replace(match_text, f"[REDACTED: {name}]")

    return redacted


def scan_file(filepath: str) -> list[dict[str, Any]]:
    """
    Scans a file for secrets.

    Args:
        filepath: Path to the file to scan

    Returns:
        List of findings (same format as scan_for_secrets)
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return scan_for_secrets(content)
    except (OSError, UnicodeDecodeError) as e:
        return [{
            "pattern_name": "scan_error",
            "line_number": 0,
            "line_content": str(e),
            "severity": "medium",
        }]
