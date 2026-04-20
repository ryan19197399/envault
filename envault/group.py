"""Group management for envault: organize keys into named groups."""

from typing import Optional


def create_group(vault_data: dict, group: str) -> dict:
    """Create an empty group if it doesn't exist."""
    vault_data.setdefault("groups", {})
    if group not in vault_data["groups"]:
        vault_data["groups"][group] = []
    return vault_data


def delete_group(vault_data: dict, group: str) -> bool:
    """Delete a group. Returns True if removed, False if not found."""
    groups = vault_data.get("groups", {})
    if group in groups:
        del groups[group]
        return True
    return False


def add_to_group(vault_data: dict, group: str, key: str) -> dict:
    """Add a key to a group. Creates group if needed. Raises if key not in vars."""
    if key not in vault_data.get("vars", {}):
        raise KeyError(f"Key '{key}' not found in vault.")
    vault_data.setdefault("groups", {})
    vault_data["groups"].setdefault(group, [])
    if key not in vault_data["groups"][group]:
        vault_data["groups"][group].append(key)
    return vault_data


def remove_from_group(vault_data: dict, group: str, key: str) -> bool:
    """Remove a key from a group. Returns True if removed, False otherwise."""
    groups = vault_data.get("groups", {})
    if group in groups and key in groups[group]:
        groups[group].remove(key)
        return True
    return False


def get_group(vault_data: dict, group: str) -> Optional[list]:
    """Return list of keys in a group, or None if group doesn't exist."""
    return vault_data.get("groups", {}).get(group)


def list_groups(vault_data: dict) -> dict:
    """Return all groups and their keys."""
    return dict(vault_data.get("groups", {}))


def key_groups(vault_data: dict, key: str) -> list:
    """Return all groups that contain the given key."""
    return [
        group
        for group, keys in vault_data.get("groups", {}).items()
        if key in keys
    ]
