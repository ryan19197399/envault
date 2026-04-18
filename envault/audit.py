"""Audit log for vault operations."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


def _audit_path(vault_name: str, base_dir: Optional[str] = None) -> Path:
    base = Path(base_dir) if base_dir else Path.home() / ".envault"
    return base / f"{vault_name}.audit.jsonl"


def log_event(vault_name: str, action: str, key: Optional[str] = None,
              base_dir: Optional[str] = None) -> None:
    """Append an audit event to the vault's audit log."""
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "vault": vault_name,
        "action": action,
    }
    if key is not None:
        entry["key"] = key

    path = _audit_path(vault_name, base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(entry) + "\n")


def read_log(vault_name: str, base_dir: Optional[str] = None) -> list[dict]:
    """Read all audit events for a vault."""
    path = _audit_path(vault_name, base_dir)
    if not path.exists():
        return []
    events = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def clear_log(vault_name: str, base_dir: Optional[str] = None) -> None:
    """Delete the audit log for a vault."""
    path = _audit_path(vault_name, base_dir)
    if path.exists():
        path.unlink()
