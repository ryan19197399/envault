"""Lifecycle hooks: run shell commands before/after vault key access or mutation."""

from __future__ import annotations

from typing import Literal

HookEvent = Literal["pre_get", "post_get", "pre_set", "post_set", "pre_delete", "post_delete"]

VALID_EVENTS: tuple[str, ...] = (
    "pre_get", "post_get",
    "pre_set", "post_set",
    "pre_delete", "post_delete",
)


def set_hook(vault_data: dict, key: str, event: str, command: str) -> None:
    """Register a shell command to run for *event* on *key*."""
    if key not in vault_data.get("vars", {}):
        raise KeyError(f"Key '{key}' not found in vault.")
    if event not in VALID_EVENTS:
        raise ValueError(f"Invalid event '{event}'. Choose from: {', '.join(VALID_EVENTS)}")
    hooks = vault_data.setdefault("lifecycle", {})
    key_hooks = hooks.setdefault(key, {})
    key_hooks[event] = command


def remove_hook(vault_data: dict, key: str, event: str) -> bool:
    """Remove a hook for *event* on *key*. Returns True if removed."""
    hooks = vault_data.get("lifecycle", {})
    key_hooks = hooks.get(key, {})
    if event in key_hooks:
        del key_hooks[event]
        if not key_hooks:
            del hooks[key]
        return True
    return False


def get_hook(vault_data: dict, key: str, event: str) -> str | None:
    """Return the command registered for *event* on *key*, or None."""
    return vault_data.get("lifecycle", {}).get(key, {}).get(event)


def list_hooks(vault_data: dict, key: str) -> dict[str, str]:
    """Return all hooks registered for *key*."""
    return dict(vault_data.get("lifecycle", {}).get(key, {}))


def fire_hook(vault_data: dict, key: str, event: str) -> str | None:
    """Execute the hook command for *event* on *key* if one exists.

    Returns the command string that was run, or None.
    """
    import subprocess
    command = get_hook(vault_data, key, event)
    if command is None:
        return None
    subprocess.run(command, shell=True, check=False)  # noqa: S602
    return command
