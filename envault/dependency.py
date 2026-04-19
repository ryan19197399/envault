"""Manage dependencies between vault keys."""

from typing import Optional


def add_dependency(vault_data: dict, key: str, depends_on: str) -> None:
    """Record that `key` depends on `depends_on`."""
    if key not in vault_data.get("vars", {}):
        raise KeyError(f"Key '{key}' not found in vault.")
    if depends_on not in vault_data.get("vars", {}):
        raise KeyError(f"Key '{depends_on}' not found in vault.")
    deps = vault_data.setdefault("dependencies", {})
    dependents = deps.setdefault(key, [])
    if depends_on not in dependents:
        dependents.append(depends_on)


def remove_dependency(vault_data: dict, key: str, depends_on: str) -> bool:
    """Remove a dependency. Returns True if removed, False if not found."""
    deps = vault_data.get("dependencies", {})
    dependents = deps.get(key, [])
    if depends_on in dependents:
        dependents.remove(depends_on)
        if not dependents:
            del deps[key]
        return True
    return False


def get_dependencies(vault_data: dict, key: str) -> list:
    """Return list of keys that `key` depends on."""
    return vault_data.get("dependencies", {}).get(key, [])


def get_dependents(vault_data: dict, key: str) -> list:
    """Return list of keys that depend on `key`."""
    return [
        k for k, deps in vault_data.get("dependencies", {}).items()
        if key in deps
    ]


def list_all_dependencies(vault_data: dict) -> dict:
    """Return the full dependency map."""
    return dict(vault_data.get("dependencies", {}))


def check_missing_dependencies(vault_data: dict) -> dict:
    """Return keys whose dependencies reference missing vault keys."""
    vars_keys = set(vault_data.get("vars", {}).keys())
    result = {}
    for key, deps in vault_data.get("dependencies", {}).items():
        missing = [d for d in deps if d not in vars_keys]
        if missing:
            result[key] = missing
    return result
