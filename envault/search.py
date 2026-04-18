"""Search and filter vault variables by key pattern, value pattern, or tag."""

import fnmatch
from typing import Optional


def search_keys(vault_data: dict, pattern: str) -> dict:
    """Return variables whose keys match a glob pattern."""
    vars_ = vault_data.get("vars", {})
    return {k: v for k, v in vars_.items() if fnmatch.fnmatch(k, pattern)}


def search_values(vault_data: dict, substring: str) -> dict:
    """Return variables whose values contain the given substring."""
    vars_ = vault_data.get("vars", {})
    return {k: v for k, v in vars_.items() if substring in v}


def search_by_tag(vault_data: dict, tag: str) -> dict:
    """Return variables that have the given tag assigned."""
    tags_map = vault_data.get("tags", {})
    vars_ = vault_data.get("vars", {})
    matched_keys = {k for k, tags in tags_map.items() if tag in tags}
    return {k: vars_[k] for k in matched_keys if k in vars_}


def search_combined(
    vault_data: dict,
    key_pattern: Optional[str] = None,
    value_substr: Optional[str] = None,
    tag: Optional[str] = None,
) -> dict:
    """Return variables matching ALL provided filters (AND logic)."""
    vars_ = vault_data.get("vars", {})
    result = dict(vars_)

    if key_pattern:
        result = {k: v for k, v in result.items() if fnmatch.fnmatch(k, key_pattern)}
    if value_substr:
        result = {k: v for k, v in result.items() if value_substr in v}
    if tag:
        tags_map = vault_data.get("tags", {})
        result = {k: v for k, v in result.items() if tag in tags_map.get(k, [])}

    return result
