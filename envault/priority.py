"""Priority management for vault keys.

Allows keys to be assigned a numeric priority (1=highest) so that
consumers can process or display variables in a defined order.
"""

from __future__ import annotations

DEFAULT_PRIORITY = 100
_PRIORITY_KEY = "__priorities__"


def set_priority(vault_data: dict, key: str, priority: int) -> None:
    """Assign a numeric priority to *key*.

    Lower numbers indicate higher priority.  *priority* must be >= 1.
    Raises KeyError if *key* is not present in vault vars.
    Raises ValueError if *priority* is less than 1.
    """
    if key not in vault_data.get("vars", {}):
        raise KeyError(f"Key '{key}' not found in vault.")
    if priority < 1:
        raise ValueError("Priority must be >= 1.")
    vault_data.setdefault(_PRIORITY_KEY, {})[key] = priority


def remove_priority(vault_data: dict, key: str) -> bool:
    """Remove the priority entry for *key*.  Returns True if removed."""
    priorities = vault_data.get(_PRIORITY_KEY, {})
    if key in priorities:
        del priorities[key]
        return True
    return False


def get_priority(vault_data: dict, key: str) -> int:
    """Return the priority for *key*, or DEFAULT_PRIORITY if not set."""
    return vault_data.get(_PRIORITY_KEY, {}).get(key, DEFAULT_PRIORITY)


def list_priorities(vault_data: dict) -> list[tuple[str, int]]:
    """Return all keys that have an explicit priority, sorted by priority.

    Returns a list of (key, priority) tuples ordered ascending.
    """
    priorities = vault_data.get(_PRIORITY_KEY, {})
    return sorted(priorities.items(), key=lambda kv: kv[1])


def sorted_keys(vault_data: dict) -> list[str]:
    """Return all vault variable keys sorted by their priority value.

    Keys without an explicit priority are placed last (DEFAULT_PRIORITY).
    """
    all_keys = list(vault_data.get("vars", {}).keys())
    priorities = vault_data.get(_PRIORITY_KEY, {})
    return sorted(all_keys, key=lambda k: priorities.get(k, DEFAULT_PRIORITY))
