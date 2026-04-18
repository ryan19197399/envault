"""Rename and alias key operations for envault vaults."""

from typing import Optional


def rename_key(vault_data: dict, old_key: str, new_key: str, overwrite: bool = False) -> dict:
    """Rename a key in the vault. Returns updated vault_data."""
    env = vault_data.get("env", {})

    if old_key not in env:
        raise KeyError(f"Key '{old_key}' not found in vault.")
    if new_key in env and not overwrite:
        raise ValueError(f"Key '{new_key}' already exists. Use overwrite=True to replace it.")

    env[new_key] = env.pop(old_key)

    # Migrate tags
    tags = vault_data.get("tags", {})
    if old_key in tags:
        tags[new_key] = tags.pop(old_key)

    # Migrate notes
    notes = vault_data.get("notes", {})
    if old_key in notes:
        notes[new_key] = notes.pop(old_key)

    # Migrate ttl
    ttl = vault_data.get("ttl", {})
    if old_key in ttl:
        ttl[new_key] = ttl.pop(old_key)

    return vault_data


def set_alias(vault_data: dict, key: str, alias: str) -> dict:
    """Create an alias (pointer) from alias -> key."""
    if key not in vault_data.get("env", {}):
        raise KeyError(f"Key '{key}' not found in vault.")
    aliases = vault_data.setdefault("aliases", {})
    aliases[alias] = key
    return vault_data


def remove_alias(vault_data: dict, alias: str) -> bool:
    """Remove an alias. Returns True if removed, False if not found."""
    aliases = vault_data.get("aliases", {})
    if alias in aliases:
        del aliases[alias]
        return True
    return False


def resolve_alias(vault_data: dict, key_or_alias: str) -> Optional[str]:
    """Resolve a key or alias to the actual value."""
    env = vault_data.get("env", {})
    aliases = vault_data.get("aliases", {})

    if key_or_alias in env:
        return env[key_or_alias]
    if key_or_alias in aliases:
        real_key = aliases[key_or_alias]
        return env.get(real_key)
    return None


def list_aliases(vault_data: dict) -> dict:
    """Return all alias -> key mappings."""
    return dict(vault_data.get("aliases", {}))
