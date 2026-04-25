"""Variance tracking: detect when a key's value deviates from its baseline."""

from __future__ import annotations

from typing import Optional


def set_baseline(vault_data: dict, key: str, value: Optional[str] = None) -> str:
    """Record the current (or given) value as the baseline for a key."""
    if key not in vault_data.get("vars", {}):
        raise KeyError(f"Key '{key}' not found in vault")
    baseline_value = value if value is not None else vault_data["vars"][key]
    vault_data.setdefault("variance", {})[key] = baseline_value
    return baseline_value


def remove_baseline(vault_data: dict, key: str) -> bool:
    """Remove the baseline for a key. Returns True if it existed."""
    baselines = vault_data.get("variance", {})
    if key in baselines:
        del baselines[key]
        return True
    return False


def get_baseline(vault_data: dict, key: str) -> Optional[str]:
    """Return the baseline value for a key, or None if not set."""
    return vault_data.get("variance", {}).get(key)


def check_variance(vault_data: dict, key: str) -> dict:
    """Compare current value against baseline.

    Returns a dict with keys: key, baseline, current, drifted.
    """
    if key not in vault_data.get("vars", {}):
        raise KeyError(f"Key '{key}' not found in vault")
    baseline = get_baseline(vault_data, key)
    current = vault_data["vars"][key]
    return {
        "key": key,
        "baseline": baseline,
        "current": current,
        "drifted": baseline is not None and current != baseline,
    }


def variance_report(vault_data: dict) -> list[dict]:
    """Return variance info for all keys that have a baseline set."""
    results = []
    for key in vault_data.get("variance", {}):
        if key in vault_data.get("vars", {}):
            results.append(check_variance(vault_data, key))
    results.sort(key=lambda r: r["key"])
    return results
