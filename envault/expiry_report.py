"""Generate expiry reports for vault variables with TTL or reminders."""

from datetime import datetime, timezone
from typing import Any


def _now() -> datetime:
    return datetime.now(timezone.utc)


def get_expiring_soon(vault_data: dict, within_seconds: int = 86400) -> list[dict]:
    """Return variables whose TTL expires within `within_seconds` from now."""
    ttls = vault_data.get("_ttl", {})
    now = _now()
    results = []
    for key, expiry_str in ttls.items():
        try:
            expiry = datetime.fromisoformat(expiry_str)
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            delta = (expiry - now).total_seconds()
            if 0 < delta <= within_seconds:
                results.append({"key": key, "expires_at": expiry_str, "seconds_left": int(delta)})
        except (ValueError, TypeError):
            continue
    results.sort(key=lambda r: r["seconds_left"])
    return results


def get_already_expired(vault_data: dict) -> list[dict]:
    """Return variables whose TTL has already passed."""
    ttls = vault_data.get("_ttl", {})
    now = _now()
    results = []
    for key, expiry_str in ttls.items():
        try:
            expiry = datetime.fromisoformat(expiry_str)
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            if expiry <= now:
                results.append({"key": key, "expired_at": expiry_str})
        except (ValueError, TypeError):
            continue
    return results


def get_due_reminders(vault_data: dict) -> list[dict]:
    """Return reminder entries that are due (past their due date)."""
    reminders = vault_data.get("_reminders", {})
    now = _now()
    results = []
    for key, entry in reminders.items():
        try:
            due = datetime.fromisoformat(entry["due"])
            if due.tzinfo is None:
                due = due.replace(tzinfo=timezone.utc)
            if due <= now:
                results.append({"key": key, "due": entry["due"], "message": entry.get("message", "")})
        except (KeyError, ValueError, TypeError):
            continue
    return results


def build_report(vault_data: dict, warn_within_seconds: int = 86400) -> dict[str, Any]:
    """Build a full expiry report for a vault."""
    return {
        "expiring_soon": get_expiring_soon(vault_data, warn_within_seconds),
        "already_expired": get_already_expired(vault_data),
        "due_reminders": get_due_reminders(vault_data),
    }
