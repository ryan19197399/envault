"""Lint vault variables for common issues."""

import re
from typing import Any

_UPPER_SNAKE = re.compile(r'^[A-Z][A-Z0-9_]*$')
_LOWER_OR_MIXED = re.compile(r'^[a-z]')


def lint_key_naming(vault_data: dict) -> list[dict]:
    """Warn about keys that don't follow UPPER_SNAKE_CASE convention."""
    issues = []
    for key in vault_data.get("vars", {}):
        if not _UPPER_SNAKE.match(key):
            issues.append({"key": key, "issue": "naming", "message": f"Key '{key}' is not UPPER_SNAKE_CASE"})
    return issues


def lint_empty_values(vault_data: dict) -> list[dict]:
    """Warn about keys with empty string values."""
    issues = []
    for key, val in vault_data.get("vars", {}).items():
        if val == "":
            issues.append({"key": key, "issue": "empty_value", "message": f"Key '{key}' has an empty value"})
    return issues


def lint_duplicate_values(vault_data: dict) -> list[dict]:
    """Warn about multiple keys sharing the same value."""
    seen: dict[str, list[str]] = {}
    for key, val in vault_data.get("vars", {}).items():
        seen.setdefault(val, []).append(key)
    issues = []
    for val, keys in seen.items():
        if len(keys) > 1:
            issues.append({
                "key": ", ".join(keys),
                "issue": "duplicate_value",
                "message": f"Keys {keys} share the same value"
            })
    return issues


def lint_expired_ttl(vault_data: dict) -> list[dict]:
    """Warn about keys whose TTL has expired."""
    import time
    issues = []
    for key, expiry in vault_data.get("ttl", {}).items():
        if expiry < time.time():
            issues.append({"key": key, "issue": "expired_ttl", "message": f"Key '{key}' TTL has expired"})
    return issues


def run_lint(vault_data: dict, checks: list[str] | None = None) -> list[dict]:
    """Run all (or selected) lint checks and return combined issues list."""
    all_checks = {
        "naming": lint_key_naming,
        "empty": lint_empty_values,
        "duplicates": lint_duplicate_values,
        "ttl": lint_expired_ttl,
    }
    active = checks if checks else list(all_checks)
    issues = []
    for name in active:
        if name in all_checks:
            issues.extend(all_checks[name](vault_data))
    return issues
