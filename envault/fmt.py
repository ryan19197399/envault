"""Formatting utilities for vault variable output."""
from typing import Dict, List, Optional


def format_table(data: Dict[str, str], tags: Optional[Dict[str, List[str]]] = None, notes: Optional[Dict[str, str]] = None) -> str:
    """Format vault variables as an aligned table."""
    if not data:
        return "(no variables)"

    key_w = max(len(k) for k in data) + 2
    val_w = max(len(v) for v in data.values()) + 2

    header = f"{'KEY':<{key_w}} {'VALUE':<{val_w}}"
    if tags:
        header += f" {'TAGS':<20}"
    if notes:
        header += " NOTE"
    lines = [header, "-" * len(header)]

    for key in sorted(data):
        val = data[key]
        row = f"{key:<{key_w}} {val:<{val_w}}"
        if tags:
            tag_str = ", ".join(tags.get(key, []))
            row += f" {tag_str:<20}"
        if notes:
            note_str = notes.get(key, "")
            row += f" {note_str}"
        lines.append(row)

    return "\n".join(lines)


def format_json(data: Dict[str, str]) -> str:
    """Format vault variables as JSON."""
    import json
    return json.dumps(data, indent=2, sort_keys=True)


def format_csv(data: Dict[str, str]) -> str:
    """Format vault variables as CSV."""
    lines = ["key,value"]
    for key in sorted(data):
        val = data[key].replace('"', '""')
        lines.append(f'"{key}","{val}"')
    return "\n".join(lines)


def format_output(data: Dict[str, str], fmt: str = "table", **kwargs) -> str:
    """Dispatch to the appropriate formatter."""
    if fmt == "json":
        return format_json(data)
    if fmt == "csv":
        return format_csv(data)
    return format_table(data, **kwargs)
