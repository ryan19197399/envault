"""Promote variables between named environments (e.g. dev -> staging -> prod)."""

from typing import Optional

ENV_ORDER = ["dev", "staging", "prod"]


def set_env_chain(vault_data: dict, chain: list[str]) -> None:
    """Store a custom promotion chain in vault metadata."""
    vault_data.setdefault("_meta", {})
    vault_data["_meta"]["env_chain"] = chain


def get_env_chain(vault_data: dict) -> list[str]:
    """Return the active promotion chain, falling back to default."""
    return vault_data.get("_meta", {}).get("env_chain", ENV_ORDER)


def promote_key(
    src_vault: dict,
    dst_vault: dict,
    key: str,
    overwrite: bool = False,
) -> bool:
    """Copy a single key from src to dst vault.

    Returns True if the key was promoted, False if skipped.
    Raises KeyError if the key is missing from src.
    """
    vars_ = src_vault.get("vars", {})
    if key not in vars_:
        raise KeyError(f"Key '{key}' not found in source vault.")
    dst_vars = dst_vault.setdefault("vars", {})
    if key in dst_vars and not overwrite:
        return False
    dst_vars[key] = vars_[key]
    return True


def promote_all(
    src_vault: dict,
    dst_vault: dict,
    overwrite: bool = False,
) -> dict:
    """Promote all variables from src to dst.

    Returns a summary dict with 'promoted' and 'skipped' key lists.
    """
    promoted = []
    skipped = []
    for key in src_vault.get("vars", {}):
        moved = promote_key(src_vault, dst_vault, key, overwrite=overwrite)
        (promoted if moved else skipped).append(key)
    return {"promoted": promoted, "skipped": skipped}


def next_env(vault_data: dict, current_env: str) -> Optional[str]:
    """Return the next environment in the promotion chain, or None if at the end."""
    chain = get_env_chain(vault_data)
    try:
        idx = chain.index(current_env)
    except ValueError:
        return None
    if idx + 1 >= len(chain):
        return None
    return chain[idx + 1]
