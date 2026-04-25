"""Key quality rating: score vault variables based on various heuristics."""

from __future__ import annotations

from typing import Any

from envault.lint import lint_key_naming, lint_empty_values
from envault.ttl import is_expired
from envault.immutable import is_immutable

_WEIGHTS = {
    "naming": 25,
    "non_empty": 25,
    "has_note": 15,
    "has_tag": 15,
    "not_expired": 10,
    "has_schema": 10,
}


def rate_key(vault_data: dict[str, Any], key: str) -> dict[str, Any]:
    """Return a quality score (0-100) and per-criterion breakdown for *key*."""
    if key not in vault_data.get("vars", {}):
        raise KeyError(f"Key '{key}' not found in vault")

    scores: dict[str, bool] = {}

    # naming
    bad_names = {issue["key"] for issue in lint_key_naming(vault_data)}
    scores["naming"] = key not in bad_names

    # non-empty
    empty_keys = {issue["key"] for issue in lint_empty_values(vault_data)}
    scores["non_empty"] = key not in empty_keys

    # has note
    scores["has_note"] = bool(vault_data.get("notes", {}).get(key))

    # has tag
    scores["has_tag"] = bool(vault_data.get("tags", {}).get(key))

    # not expired
    scores["not_expired"] = not is_expired(vault_data, key)

    # has schema
    scores["has_schema"] = key in vault_data.get("schema", {})

    total = sum(_WEIGHTS[k] for k, passed in scores.items() if passed)
    return {
        "key": key,
        "score": total,
        "max": 100,
        "breakdown": {k: {"passed": v, "weight": _WEIGHTS[k]} for k, v in scores.items()},
        "immutable": is_immutable(vault_data, key),
    }


def rate_all(vault_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Return ratings for every key in the vault, sorted by score descending."""
    results = [rate_key(vault_data, k) for k in vault_data.get("vars", {})]
    return sorted(results, key=lambda r: r["score"], reverse=True)


def rating_summary(vault_data: dict[str, Any]) -> dict[str, Any]:
    """Return aggregate statistics for the whole vault."""
    ratings = rate_all(vault_data)
    if not ratings:
        return {"count": 0, "average": 0, "min": 0, "max": 0}
    scores = [r["score"] for r in ratings]
    return {
        "count": len(scores),
        "average": round(sum(scores) / len(scores), 1),
        "min": min(scores),
        "max": max(scores),
    }
