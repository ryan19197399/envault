"""Cascade: propagate a key's value to dependent keys via transform rules."""
from typing import Any, Callable, Dict, List, Optional

_TRANSFORMS: Dict[str, Callable[[str], str]] = {
    "upper": str.upper,
    "lower": str.lower,
    "strip": str.strip,
}


def set_cascade(vault_data: dict, source_key: str, target_key: str, transform: Optional[str] = None) -> dict:
    """Register a cascade rule: when source_key changes, target_key is updated."""
    if source_key not in vault_data.get("vars", {}):
        raise KeyError(f"Source key '{source_key}' not found in vault.")
    if target_key not in vault_data.get("vars", {}):
        raise KeyError(f"Target key '{target_key}' not found in vault.")
    if transform is not None and transform not in _TRANSFORMS:
        raise ValueError(f"Unknown transform '{transform}'. Valid: {list(_TRANSFORMS)}.")
    vault_data.setdefault("cascade", {})
    vault_data["cascade"][source_key] = {
        "target": target_key,
        "transform": transform,
    }
    return vault_data


def remove_cascade(vault_data: dict, source_key: str) -> bool:
    """Remove a cascade rule for source_key. Returns True if removed."""
    rules = vault_data.get("cascade", {})
    if source_key in rules:
        del rules[source_key]
        return True
    return False


def get_cascade(vault_data: dict, source_key: str) -> Optional[dict]:
    """Return the cascade rule for source_key, or None."""
    return vault_data.get("cascade", {}).get(source_key)


def list_cascades(vault_data: dict) -> List[dict]:
    """Return all cascade rules as a list of dicts."""
    rules = vault_data.get("cascade", {})
    return [
        {"source": src, "target": rule["target"], "transform": rule.get("transform")}
        for src, rule in rules.items()
    ]


def apply_cascades(vault_data: dict, changed_key: str) -> List[str]:
    """Apply any cascade rules triggered by changed_key. Returns list of updated target keys."""
    updated = []
    rule = vault_data.get("cascade", {}).get(changed_key)
    if rule is None:
        return updated
    target = rule["target"]
    transform = rule.get("transform")
    source_value: str = vault_data.get("vars", {}).get(changed_key, "")
    if transform and transform in _TRANSFORMS:
        source_value = _TRANSFORMS[transform](source_value)
    vault_data.setdefault("vars", {})[target] = source_value
    updated.append(target)
    return updated
