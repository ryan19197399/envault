"""Compare vault contents against the current OS environment."""
from __future__ import annotations
import os
from typing import Any


def compare_with_env(vault_data: dict[str, Any], env: dict[str, str] | None = None) -> dict[str, list[str]]:
    """Return a report comparing vault vars to the live environment.

    Returns a dict with keys:
      - 'only_in_vault': keys present in vault but not in env
      - 'only_in_env':   keys present in env but not in vault (filtered to UPPER_SNAKE)
      - 'matching':      keys present in both with equal values
      - 'differing':     keys present in both but with different values
    """
    if env is None:
        env = dict(os.environ)

    vars_: dict[str, str] = vault_data.get("vars", {})

    vault_keys = set(vars_.keys())
    env_keys = {k for k in env if k.isupper()}

    only_in_vault = sorted(vault_keys - env_keys)
    only_in_env = sorted(env_keys - vault_keys)
    matching: list[str] = []
    differing: list[str] = []

    for key in sorted(vault_keys & env_keys):
        if vars_[key] == env[key]:
            matching.append(key)
        else:
            differing.append(key)

    return {
        "only_in_vault": only_in_vault,
        "only_in_env": only_in_env,
        "matching": matching,
        "differing": differing,
    }


def format_compare_report(report: dict[str, list[str]]) -> str:
    """Format compare report as a human-readable string."""
    lines: list[str] = []

    if report["only_in_vault"]:
        lines.append("Only in vault (not set in environment):")
        for k in report["only_in_vault"]:
            lines.append(f"  - {k}")

    if report["only_in_env"]:
        lines.append("Only in environment (not in vault):")
        for k in report["only_in_env"]:
            lines.append(f"  + {k}")

    if report["differing"]:
        lines.append("Value differs between vault and environment:")
        for k in report["differing"]:
            lines.append(f"  ~ {k}")

    if report["matching"]:
        lines.append(f"Matching: {len(report['matching'])} key(s)")

    return "\n".join(lines) if lines else "Vault and environment are in sync."
