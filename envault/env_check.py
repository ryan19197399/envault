"""Check vault variables against the current environment."""
from typing import Dict, List


def check_missing(vault_vars: Dict[str, str], env: Dict[str, str]) -> List[str]:
    """Return keys present in vault but missing from env."""
    return [k for k in vault_vars if k not in env]


def check_extra(vault_vars: Dict[str, str], env: Dict[str, str]) -> List[str]:
    """Return keys present in env but not in vault."""
    return [k for k in env if k not in vault_vars]


def check_mismatched(vault_vars: Dict[str, str], env: Dict[str, str]) -> List[str]:
    """Return keys present in both but with differing values."""
    return [k for k in vault_vars if k in env and vault_vars[k] != env[k]]


def check_env(
    vault_vars: Dict[str, str],
    env: Dict[str, str],
) -> Dict[str, List[str]]:
    """Run all checks and return a report dict."""
    return {
        "missing": check_missing(vault_vars, env),
        "extra": check_extra(vault_vars, env),
        "mismatched": check_mismatched(vault_vars, env),
    }
