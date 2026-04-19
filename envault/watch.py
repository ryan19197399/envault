"""Watch a vault for changes and trigger a callback."""
import time
import os
from typing import Callable, Optional
from envault.storage import _vault_path


def get_vault_mtime(vault_name: str, base_dir: Optional[str] = None) -> Optional[float]:
    """Return the last modified time of the vault file, or None if missing."""
    path = _vault_path(vault_name, base_dir)
    try:
        return os.path.getmtime(path)
    except FileNotFoundError:
        return None


def watch_vault(
    vault_name: str,
    callback: Callable[[str], None],
    interval: float = 1.0,
    max_checks: Optional[int] = None,
    base_dir: Optional[str] = None,
) -> None:
    """Poll the vault file and call callback(vault_name) when it changes.

    Args:
        vault_name: Name of the vault to watch.
        callback: Function called with vault_name when a change is detected.
        interval: Polling interval in seconds.
        max_checks: Stop after this many checks (None = run forever).
        base_dir: Override default vault directory.
    """
    last_mtime = get_vault_mtime(vault_name, base_dir)
    checks = 0

    while max_checks is None or checks < max_checks:
        time.sleep(interval)
        current_mtime = get_vault_mtime(vault_name, base_dir)
        if current_mtime != last_mtime:
            last_mtime = current_mtime
            callback(vault_name)
        checks += 1
