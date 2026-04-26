"""Policy engine for envault — define and enforce rules on vault keys.

Policies allow you to specify constraints such as minimum length,
required prefixes/suffixes, regex patterns, and forbidden values
for any key in the vault.
"""

import re
from typing import Any

# Internal key used to store policies inside vault data
_POLICY_KEY = "__policies__"

# Supported rule types
SUPPORTED_RULES = {"min_length", "max_length", "pattern", "prefix", "suffix", "forbidden"}


def define_policy(vault_data: dict, key: str, rules: dict) -> None:
    """Attach a policy (set of rules) to a vault key.

    Args:
        vault_data: The vault data dict (mutated in place).
        key: The vault key to attach the policy to.
        rules: A dict of rule_name -> rule_value pairs.

    Raises:
        KeyError: If the key does not exist in vault vars.
        ValueError: If any rule name is unsupported.
    """
    vars_ = vault_data.get("vars", {})
    if key not in vars_:
        raise KeyError(f"Key '{key}' not found in vault")

    unknown = set(rules) - SUPPORTED_RULES
    if unknown:
        raise ValueError(f"Unsupported rule(s): {', '.join(sorted(unknown))}")

    policies = vault_data.setdefault(_POLICY_KEY, {})
    policies[key] = dict(rules)


def remove_policy(vault_data: dict, key: str) -> bool:
    """Remove the policy for a vault key.

    Returns:
        True if a policy was removed, False if none existed.
    """
    policies = vault_data.get(_POLICY_KEY, {})
    if key in policies:
        del policies[key]
        return True
    return False


def get_policy(vault_data: dict, key: str) -> dict | None:
    """Return the policy dict for a key, or None if not set."""
    return vault_data.get(_POLICY_KEY, {}).get(key)


def list_policies(vault_data: dict) -> dict:
    """Return all policies keyed by vault key name."""
    return dict(vault_data.get(_POLICY_KEY, {}))


def validate_key(vault_data: dict, key: str) -> list[str]:
    """Validate a vault key's current value against its policy.

    Args:
        vault_data: The vault data dict.
        key: The vault key to validate.

    Returns:
        A list of violation messages (empty list means the key passes).
    """
    policy = get_policy(vault_data, key)
    if not policy:
        return []

    value: Any = vault_data.get("vars", {}).get(key, "")
    violations: list[str] = []

    if "min_length" in policy:
        if len(str(value)) < int(policy["min_length"]):
            violations.append(
                f"Value too short: minimum length is {policy['min_length']}"
            )

    if "max_length" in policy:
        if len(str(value)) > int(policy["max_length"]):
            violations.append(
                f"Value too long: maximum length is {policy['max_length']}"
            )

    if "prefix" in policy:
        if not str(value).startswith(policy["prefix"]):
            violations.append(f"Value must start with '{policy['prefix']}'")

    if "suffix" in policy:
        if not str(value).endswith(policy["suffix"]):
            violations.append(f"Value must end with '{policy['suffix']}'")

    if "pattern" in policy:
        if not re.search(policy["pattern"], str(value)):
            violations.append(f"Value does not match pattern '{policy['pattern']}'")

    if "forbidden" in policy:
        forbidden = policy["forbidden"]
        if isinstance(forbidden, str):
            forbidden = [forbidden]
        if str(value) in forbidden:
            violations.append(f"Value '{value}' is explicitly forbidden by policy")

    return violations


def validate_all(vault_data: dict) -> dict[str, list[str]]:
    """Validate all keys that have policies.

    Returns:
        A dict mapping key -> list of violation strings.
        Only keys with at least one violation are included.
    """
    results: dict[str, list[str]] = {}
    for key in vault_data.get(_POLICY_KEY, {}):
        violations = validate_key(vault_data, key)
        if violations:
            results[key] = violations
    return results
