"""Redaction utilities for masking sensitive vault values in output."""

import re
from typing import Any

DEFAULT_SENSITIVE_PATTERNS = [
    re.compile(r"(password|passwd|secret|token|api[_-]?key|private[_-]?key|auth)", re.IGNORECASE),
]

REDACT_PLACEHOLDER = "***REDACTED***"


def is_sensitive(key: str, patterns: list = None) -> bool:
    """Return True if the key name matches any sensitive pattern."""
    if patterns is None:
        patterns = DEFAULT_SENSITIVE_PATTERNS
    return any(p.search(key) for p in patterns)


def redact_value(key: str, value: str, patterns: list = None) -> str:
    """Return redacted placeholder if key is sensitive, otherwise return value."""
    if is_sensitive(key, patterns):
        return REDACT_PLACEHOLDER
    return value


def redact_dict(
    data: dict[str, Any],
    patterns: list = None,
    keys_only: list = None,
) -> dict[str, Any]:
    """Return a copy of data with sensitive values replaced by the placeholder.

    Args:
        data: Flat dict of key -> value pairs.
        patterns: Optional list of compiled regex patterns to detect sensitive keys.
        keys_only: If provided, only redact these specific keys regardless of patterns.
    """
    result = {}
    for k, v in data.items():
        if keys_only is not None:
            result[k] = REDACT_PLACEHOLDER if k in keys_only else v
        else:
            result[k] = redact_value(k, v, patterns)
    return result


def redact_vault_vars(vault_data: dict, **kwargs) -> dict[str, str]:
    """Convenience wrapper: extract 'vars' from vault_data and redact them."""
    raw = vault_data.get("vars", {})
    return redact_dict(raw, **kwargs)
