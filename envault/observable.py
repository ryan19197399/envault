"""Observable variables: trigger actions when a key's value changes."""

from typing import Any, Dict, List, Optional

_KEY = "_observables"


def set_observer(vault_data: dict, key: str, action: str, target: Optional[str] = None) -> None:
    """Register an observer action for a key.

    Args:
        vault_data: The vault dict.
        key: The variable key to observe.
        action: One of 'log', 'copy', 'notify'.
        target: Optional target key (used with 'copy').
    """
    valid_actions = {"log", "copy", "notify"}
    if action not in valid_actions:
        raise ValueError(f"Invalid action '{action}'. Must be one of: {', '.join(sorted(valid_actions))}")
    if key not in vault_data.get("vars", {}):
        raise KeyError(f"Key '{key}' not found in vault.")
    if action == "copy" and not target:
        raise ValueError("Action 'copy' requires a target key.")
    if action == "copy" and target not in vault_data.get("vars", {}):
        raise KeyError(f"Target key '{target}' not found in vault.")

    observables = vault_data.setdefault(_KEY, {})
    entry = {"action": action}
    if target:
        entry["target"] = target
    observables[key] = entry


def remove_observer(vault_data: dict, key: str) -> bool:
    """Remove observer for a key. Returns True if removed, False if not found."""
    observables = vault_data.get(_KEY, {})
    if key in observables:
        del observables[key]
        return True
    return False


def get_observer(vault_data: dict, key: str) -> Optional[Dict[str, Any]]:
    """Return observer entry for a key, or None."""
    return vault_data.get(_KEY, {}).get(key)


def list_observers(vault_data: dict) -> List[Dict[str, Any]]:
    """Return all observers as a list of dicts with 'key', 'action', optional 'target'."""
    result = []
    for key, entry in vault_data.get(_KEY, {}).items():
        row = {"key": key, **entry}
        result.append(row)
    return result


def fire_observers(vault_data: dict, key: str, old_value: Any, new_value: Any) -> List[str]:
    """Execute observers for a changed key. Returns list of action log strings."""
    observer = vault_data.get(_KEY, {}).get(key)
    if not observer:
        return []

    logs = []
    action = observer["action"]

    if action == "log":
        logs.append(f"[observe] {key} changed: {old_value!r} -> {new_value!r}")

    elif action == "copy":
        target = observer.get("target")
        if target and target in vault_data.get("vars", {}):
            vault_data["vars"][target] = new_value
            logs.append(f"[observe] {key} copied to {target}: {new_value!r}")

    elif action == "notify":
        logs.append(f"[observe] NOTIFY: {key} changed to {new_value!r}")

    return logs
