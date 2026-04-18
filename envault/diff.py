"""Diff utilities for comparing vault states."""
from typing import Any


def diff_vaults(old: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    """Compare two vault variable dicts and return a structured diff."""
    old_vars = old.get("vars", {})
    new_vars = new.get("vars", {})

    added = {k: new_vars[k] for k in new_vars if k not in old_vars}
    removed = {k: old_vars[k] for k in old_vars if k not in new_vars}
    changed = {
        k: {"old": old_vars[k], "new": new_vars[k]}
        for k in old_vars
        if k in new_vars and old_vars[k] != new_vars[k]
    }
    unchanged = {
        k: old_vars[k]
        for k in old_vars
        if k in new_vars and old_vars[k] == new_vars[k]
    }

    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged": unchanged,
    }


def format_diff(diff: dict[str, Any], show_unchanged: bool = False) -> str:
    """Format a diff dict as a human-readable string."""
    lines = []

    for key, value in diff["added"].items():
        lines.append(f"+ {key}={value}")

    for key, value in diff["removed"].items():
        lines.append(f"- {key}={value}")

    for key, values in diff["changed"].items():
        lines.append(f"~ {key}: {values['old']} -> {values['new']}")

    if show_unchanged:
        for key, value in diff["unchanged"].items():
            lines.append(f"  {key}={value}")

    return "\n".join(lines) if lines else "(no differences)"
