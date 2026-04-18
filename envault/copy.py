"""Copy/clone variables between vaults."""

from envault.vault import Vault
from envault.storage import vault_exists


def copy_key(src_vault: dict, dst_vault: dict, key: str, overwrite: bool = False) -> bool:
    """Copy a single key from src to dst vault data. Returns True if copied."""
    env = src_vault.get("env", {})
    if key not in env:
        raise KeyError(f"Key '{key}' not found in source vault")
    dst_env = dst_vault.setdefault("env", {})
    if key in dst_env and not overwrite:
        return False
    dst_env[key] = env[key]
    return True


def copy_keys(src_vault: dict, dst_vault: dict, keys: list[str], overwrite: bool = False) -> dict:
    """Copy multiple keys. Returns dict with key -> 'copied'|'skipped'|'missing'."""
    results = {}
    for key in keys:
        try:
            copied = copy_key(src_vault, dst_vault, key, overwrite=overwrite)
            results[key] = "copied" if copied else "skipped"
        except KeyError:
            results[key] = "missing"
    return results


def clone_vault(src_vault: dict, dst_vault: dict, overwrite: bool = False) -> dict:
    """Clone all keys from src to dst vault. Returns copy results."""
    keys = list(src_vault.get("env", {}).keys())
    return copy_keys(src_vault, dst_vault, keys, overwrite=overwrite)
