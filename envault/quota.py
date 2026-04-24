"""Quota management: enforce per-vault key count and value size limits."""

from __future__ import annotations

DEFAULT_MAX_KEYS = 500
DEFAULT_MAX_VALUE_BYTES = 4096

_QUOTA_KEY = "__quota__"


def set_quota(vault_data: dict, max_keys: int | None = None, max_value_bytes: int | None = None) -> dict:
    """Set quota settings on the vault."""
    quota = vault_data.setdefault(_QUOTA_KEY, {})
    if max_keys is not None:
        if max_keys < 1:
            raise ValueError("max_keys must be at least 1")
        quota["max_keys"] = max_keys
    if max_value_bytes is not None:
        if max_value_bytes < 1:
            raise ValueError("max_value_bytes must be at least 1")
        quota["max_value_bytes"] = max_value_bytes
    return vault_data


def get_quota(vault_data: dict) -> dict:
    """Return current quota settings with defaults filled in."""
    quota = vault_data.get(_QUOTA_KEY, {})
    return {
        "max_keys": quota.get("max_keys", DEFAULT_MAX_KEYS),
        "max_value_bytes": quota.get("max_value_bytes", DEFAULT_MAX_VALUE_BYTES),
    }


def remove_quota(vault_data: dict) -> bool:
    """Remove quota settings, reverting to defaults. Returns True if existed."""
    if _QUOTA_KEY in vault_data:
        del vault_data[_QUOTA_KEY]
        return True
    return False


def check_quota(vault_data: dict, new_key: str, new_value: str) -> None:
    """Raise ValueError if adding new_key=new_value would violate quota."""
    quota = get_quota(vault_data)
    vars_ = vault_data.get("vars", {})

    # Count keys excluding the one being set (allow updates)
    existing_keys = set(vars_.keys())
    if new_key not in existing_keys and len(existing_keys) >= quota["max_keys"]:
        raise ValueError(
            f"Quota exceeded: vault already has {len(existing_keys)} keys "
            f"(max {quota['max_keys']})"
        )

    value_bytes = len(new_value.encode("utf-8"))
    if value_bytes > quota["max_value_bytes"]:
        raise ValueError(
            f"Quota exceeded: value for '{new_key}' is {value_bytes} bytes "
            f"(max {quota['max_value_bytes']})"
        )


def quota_report(vault_data: dict) -> dict:
    """Return a usage report dict."""
    quota = get_quota(vault_data)
    vars_ = vault_data.get("vars", {})
    key_count = len(vars_)
    max_value = max((len(v.encode()) for v in vars_.values()), default=0)
    return {
        "key_count": key_count,
        "max_keys": quota["max_keys"],
        "keys_remaining": max(0, quota["max_keys"] - key_count),
        "max_value_bytes": quota["max_value_bytes"],
        "largest_value_bytes": max_value,
    }
