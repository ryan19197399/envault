"""Snapshot and restore environment variable states."""
from datetime import datetime
from typing import Optional

SNAPSHOTS_KEY = "__snapshots__"


def create_snapshot(vault_data: dict, name: Optional[str] = None) -> str:
    """Create a named snapshot of current vault vars. Returns snapshot name."""
    if SNAPSHOTS_KEY not in vault_data:
        vault_data[SNAPSHOTS_KEY] = {}

    name = name or datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    vars_copy = {
        k: v for k, v in vault_data.get("vars", {}).items()
    }
    vault_data[SNAPSHOTS_KEY][name] = {
        "created_at": datetime.utcnow().isoformat(),
        "vars": vars_copy,
    }
    return name


def restore_snapshot(vault_data: dict, name: str) -> bool:
    """Restore vars from a named snapshot. Returns True if successful."""
    snapshots = vault_data.get(SNAPSHOTS_KEY, {})
    if name not in snapshots:
        return False
    vault_data["vars"] = dict(snapshots[name]["vars"])
    return True


def delete_snapshot(vault_data: dict, name: str) -> bool:
    """Delete a named snapshot. Returns True if it existed."""
    snapshots = vault_data.get(SNAPSHOTS_KEY, {})
    if name not in snapshots:
        return False
    del snapshots[name]
    return True


def list_snapshots(vault_data: dict) -> list:
    """Return list of (name, created_at) tuples."""
    snapshots = vault_data.get(SNAPSHOTS_KEY, {})
    return [
        (name, meta["created_at"])
        for name, meta in sorted(snapshots.items(), key=lambda x: x[1]["created_at"])
    ]


def get_snapshot(vault_data: dict, name: str) -> Optional[dict]:
    """Return snapshot vars dict or None."""
    snapshots = vault_data.get(SNAPSHOTS_KEY, {})
    entry = snapshots.get(name)
    return entry["vars"] if entry else None
