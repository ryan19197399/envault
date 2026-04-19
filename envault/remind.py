"""Reminders: attach due-date reminders to vault keys."""
from datetime import datetime, timezone
from typing import Optional

REMINDERS_KEY = "__reminders__"
DT_FMT = "%Y-%m-%dT%H:%M:%S"


def set_reminder(vault_data: dict, key: str, due: datetime, message: str = "") -> dict:
    """Attach a reminder to a vault key."""
    if key not in vault_data.get("vars", {}):
        raise KeyError(f"Key '{key}' not found in vault")
    vault_data.setdefault(REMINDERS_KEY, {})
    vault_data[REMINDERS_KEY][key] = {
        "due": due.strftime(DT_FMT),
        "message": message,
    }
    return vault_data


def remove_reminder(vault_data: dict, key: str) -> bool:
    """Remove a reminder from a vault key. Returns True if removed."""
    reminders = vault_data.get(REMINDERS_KEY, {})
    if key in reminders:
        del reminders[key]
        return True
    return False


def get_reminder(vault_data: dict, key: str) -> Optional[dict]:
    """Return reminder dict for key, or None."""
    return vault_data.get(REMINDERS_KEY, {}).get(key)


def list_due(vault_data: dict, as_of: Optional[datetime] = None) -> list:
    """Return list of (key, reminder) tuples that are due as of *as_of* (default: now)."""
    if as_of is None:
        as_of = datetime.now(timezone.utc).replace(tzinfo=None)
    results = []
    for key, entry in vault_data.get(REMINDERS_KEY, {}).items():
        due_dt = datetime.strptime(entry["due"], DT_FMT)
        if due_dt <= as_of:
            results.append((key, entry))
    return results


def list_reminders(vault_data: dict) -> list:
    """Return all reminders as list of (key, reminder) tuples."""
    return list(vault_data.get(REMINDERS_KEY, {}).items())
