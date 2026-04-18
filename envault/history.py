"""History tracking for variable changes in a vault."""

from datetime import datetime, timezone
from typing import Optional

HISTORY_KEY = "__history__"
MAX_HISTORY = 100


def record_change(
    vault_data: dict,
    key: str,
    action: str,
    old_value: Optional[str] = None,
    new_value: Optional[str] = None,
) -> dict:
    """Record a change event for a key in vault history."""
    if HISTORY_KEY not in vault_data:
        vault_data[HISTORY_KEY] = []

    entry = {
        "key": key,
        "action": action,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if old_value is not None:
        entry["old_value"] = old_value
    if new_value is not None:
        entry["new_value"] = new_value

    vault_data[HISTORY_KEY].append(entry)

    if len(vault_data[HISTORY_KEY]) > MAX_HISTORY:
        vault_data[HISTORY_KEY] = vault_data[HISTORY_KEY][-MAX_HISTORY:]

    return vault_data


def get_history(vault_data: dict, key: Optional[str] = None) -> list:
    """Return history entries, optionally filtered by key."""
    entries = vault_data.get(HISTORY_KEY, [])
    if key is not None:
        entries = [e for e in entries if e["key"] == key]
    return entries


def clear_history(vault_data: dict, key: Optional[str] = None) -> dict:
    """Clear all history or history for a specific key."""
    if key is None:
        vault_data[HISTORY_KEY] = []
    else:
        vault_data[HISTORY_KEY] = [
            e for e in vault_data.get(HISTORY_KEY, []) if e["key"] != key
        ]
    return vault_data
