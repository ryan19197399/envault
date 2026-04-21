"""Immutable (read-only) key management for envault vaults."""

from typing import List

_IMMUTABLE_KEY = "_immutable"


def mark_immutable(vault_data: dict, key: str) -> None:
    """Mark a key as immutable (read-only). Raises KeyError if key does not exist."""
    if key not in vault_data.get("vars", {}):
        raise KeyError(f"Key '{key}' does not exist in vault.")
    immutable = vault_data.setdefault(_IMMUTABLE_KEY, [])
    if key not in immutable:
        immutable.append(key)


def unmark_immutable(vault_data: dict, key: str) -> bool:
    """Remove immutable flag from a key. Returns True if removed, False if not found."""
    immutable = vault_data.get(_IMMUTABLE_KEY, [])
    if key in immutable:
        immutable.remove(key)
        return True
    return False


def is_immutable(vault_data: dict, key: str) -> bool:
    """Return True if the given key is marked as immutable."""
    return key in vault_data.get(_IMMUTABLE_KEY, [])


def list_immutable(vault_data: dict) -> List[str]:
    """Return all keys currently marked as immutable."""
    return list(vault_data.get(_IMMUTABLE_KEY, []))


def guard_immutable(vault_data: dict, key: str) -> None:
    """Raise a PermissionError if the key is immutable."""
    if is_immutable(vault_data, key):
        raise PermissionError(f"Key '{key}' is immutable and cannot be modified or deleted.")
