"""Inject vault variables into a subprocess environment."""

import os
import subprocess
from typing import Optional

from envault.vault import Vault
from envault.ttl import is_expired


def build_env(
    vault_data: dict,
    base_env: Optional[dict] = None,
    overwrite: bool = True,
    skip_expired: bool = True,
) -> dict:
    """Build an environment dict from vault variables.

    Args:
        vault_data: Raw vault dict.
        base_env: Base environment to merge into. Defaults to os.environ copy.
        overwrite: If False, existing env vars are preserved.
        skip_expired: If True, keys with expired TTL are excluded.

    Returns:
        Merged environment dict.
    """
    env = dict(base_env if base_env is not None else os.environ)
    variables = vault_data.get("vars", {})

    for key, value in variables.items():
        if skip_expired and is_expired(vault_data, key):
            continue
        if not overwrite and key in env:
            continue
        env[key] = value

    return env


def run_with_vault(
    vault_data: dict,
    command: list,
    overwrite: bool = True,
    skip_expired: bool = True,
) -> subprocess.CompletedProcess:
    """Run a shell command with vault variables injected into the environment.

    Args:
        vault_data: Raw vault dict.
        command: Command and arguments as a list.
        overwrite: Whether vault vars override existing env vars.
        skip_expired: Whether to skip expired TTL keys.

    Returns:
        CompletedProcess result.
    """
    env = build_env(vault_data, overwrite=overwrite, skip_expired=skip_expired)
    return subprocess.run(command, env=env)
