"""Conditional variables: set a var's value based on another var's value."""

from typing import Optional

_CONDVAR_KEY = "__condvars__"


def set_condvar(vault_data: dict, key: str, source_key: str, conditions: dict, default: Optional[str] = None) -> dict:
    """Define a conditional variable rule.

    conditions: mapping of source_key value -> resulting value for key.
    default: value to use when no condition matches (None means leave unset).
    """
    if key not in vault_data.get("vars", {}):
        raise KeyError(f"Key '{key}' not found in vault")
    if source_key not in vault_data.get("vars", {}):
        raise KeyError(f"Source key '{source_key}' not found in vault")
    if not conditions:
        raise ValueError("conditions must not be empty")

    vault_data.setdefault(_CONDVAR_KEY, {})
    vault_data[_CONDVAR_KEY][key] = {
        "source": source_key,
        "conditions": conditions,
        "default": default,
    }
    return vault_data


def remove_condvar(vault_data: dict, key: str) -> bool:
    """Remove a conditional variable rule. Returns True if removed."""
    rules = vault_data.get(_CONDVAR_KEY, {})
    if key in rules:
        del rules[key]
        return True
    return False


def get_condvar(vault_data: dict, key: str) -> Optional[dict]:
    """Return the condvar rule for key, or None."""
    return vault_data.get(_CONDVAR_KEY, {}).get(key)


def list_condvars(vault_data: dict) -> dict:
    """Return all condvar rules."""
    return dict(vault_data.get(_CONDVAR_KEY, {}))


def apply_condvars(vault_data: dict) -> dict:
    """Evaluate all condvar rules and update vars in-place. Returns vault_data."""
    rules = vault_data.get(_CONDVAR_KEY, {})
    vars_ = vault_data.get("vars", {})
    for key, rule in rules.items():
        source_val = vars_.get(rule["source"])
        new_val = rule["conditions"].get(source_val, rule.get("default"))
        if new_val is not None:
            vars_[key] = new_val
    vault_data["vars"] = vars_
    return vault_data
