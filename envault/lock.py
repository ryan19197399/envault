"""Vault locking: time-based session lock after inactivity."""

import time
from pathlib import Path
from typing import Optional

DEFAULT_TIMEOUT = 300  # seconds


def _lock_path(vault_dir: str, vault_name: str) -> Path:
    return Path(vault_dir) / f"{vault_name}.lock"


def touch_session(vault_dir: str, vault_name: str) -> None:
    """Update the last-active timestamp for a vault session."""
    path = _lock_path(vault_dir, vault_name)
    path.write_text(str(time.time()))


def is_locked(vault_dir: str, vault_name: str, timeout: int = DEFAULT_TIMEOUT) -> bool:
    """Return True if the vault session has expired or was never started."""
    path = _lock_path(vault_dir, vault_name)
    if not path.exists():
        return True
    try:
        last_active = float(path.read_text().strip())
    except (ValueError, OSError):
        return True
    return (time.time() - last_active) > timeout


def unlock(vault_dir: str, vault_name: str) -> None:
    """Mark vault as actively unlocked (alias for touch_session)."""
    touch_session(vault_dir, vault_name)


def lock(vault_dir: str, vault_name: str) -> None:
    """Explicitly lock the vault by removing the session file."""
    path = _lock_path(vault_dir, vault_name)
    if path.exists():
        path.unlink()


def get_last_active(vault_dir: str, vault_name: str) -> Optional[float]:
    """Return the last-active timestamp or None if not set."""
    path = _lock_path(vault_dir, vault_name)
    if not path.exists():
        return None
    try:
        return float(path.read_text().strip())
    except (ValueError, OSError):
        return None
