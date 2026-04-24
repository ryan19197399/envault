"""Variable interpolation: resolve ${VAR} references within vault values."""

import re
from typing import Optional

_REF_RE = re.compile(r"\$\{([^}]+)\}")


def resolve_value(value: str, vars_: dict, *, max_depth: int = 10) -> str:
    """Recursively expand ${KEY} references in *value* using *vars_*.

    Raises ValueError on circular references or unresolved keys.
    """
    seen: set = set()

    def _expand(v: str, depth: int) -> str:
        if depth > max_depth:
            raise ValueError("Maximum interpolation depth exceeded (circular reference?)")
        def _replace(m: re.Match) -> str:
            key = m.group(1)
            if key in seen:
                raise ValueError(f"Circular reference detected for key '{key}'")
            if key not in vars_:
                raise KeyError(f"Unresolved reference: '{{{key}}}'")
            seen.add(key)
            result = _expand(vars_[key], depth + 1)
            seen.discard(key)
            return result
        return _REF_RE.sub(_replace, v)

    return _expand(value, 0)


def resolve_all(vars_: dict, *, skip_errors: bool = False) -> dict:
    """Return a new dict with all values fully interpolated.

    If *skip_errors* is True, unresolvable values are left as-is.
    """
    resolved = {}
    for key, value in vars_.items():
        if not isinstance(value, str):
            resolved[key] = value
            continue
        try:
            resolved[key] = resolve_value(value, vars_)
        except (KeyError, ValueError):
            if skip_errors:
                resolved[key] = value
            else:
                raise
    return resolved


def has_references(value: str) -> bool:
    """Return True if *value* contains at least one ${...} placeholder."""
    return bool(_REF_RE.search(value))


def list_references(value: str) -> list:
    """Return all key names referenced in *value*."""
    return _REF_RE.findall(value)
