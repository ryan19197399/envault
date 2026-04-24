"""Chain execution: run a sequence of vault key lookups/transforms as a pipeline."""
from __future__ import annotations
from typing import Any


def set_chain(vault_data: dict, name: str, steps: list[str]) -> None:
    """Define a named chain of key references or transform steps."""
    if not steps:
        raise ValueError("Chain must have at least one step.")
    chains = vault_data.setdefault("_chains", {})
    chains[name] = {"steps": list(steps)}


def remove_chain(vault_data: dict, name: str) -> bool:
    """Remove a named chain. Returns True if it existed."""
    chains = vault_data.get("_chains", {})
    if name in chains:
        del chains[name]
        return True
    return False


def get_chain(vault_data: dict, name: str) -> list[str] | None:
    """Return the steps of a named chain, or None if not found."""
    chains = vault_data.get("_chains", {})
    entry = chains.get(name)
    if entry is None:
        return None
    return entry["steps"]


def list_chains(vault_data: dict) -> list[str]:
    """Return all defined chain names."""
    return list(vault_data.get("_chains", {}).keys())


def run_chain(vault_data: dict, name: str) -> list[Any]:
    """Execute a chain: resolve each step as a vault key and return values."""
    steps = get_chain(vault_data, name)
    if steps is None:
        raise KeyError(f"Chain '{name}' not found.")
    vars_ = vault_data.get("vars", {})
    results = []
    for step in steps:
        if step not in vars_:
            raise KeyError(f"Key '{step}' not found in vault.")
        results.append(vars_[step])
    return results
