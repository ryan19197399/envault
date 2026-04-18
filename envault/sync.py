"""Sync vault data to/from a shareable encrypted file."""

import json
from pathlib import Path
from typing import Optional

from envault.crypto import encrypt, decrypt
from envault.vault import Vault


def export_vault(vault: Vault, password: str, output_path: Path) -> None:
    """Encrypt and export vault contents to a portable file."""
    payload = json.dumps(vault.data).encode()
    token = encrypt(payload, password)
    output_path.write_bytes(token)


def import_vault(
    input_path: Path,
    password: str,
    vault_name: str,
    overwrite: bool = False,
) -> Vault:
    """Decrypt an exported vault file and load it into local storage."""
    from envault.storage import vault_exists

    if vault_exists(vault_name) and not overwrite:
        raise FileExistsError(
            f"Vault '{vault_name}' already exists. Use overwrite=True to replace it."
        )

    token = input_path.read_bytes()
    raw = decrypt(token, password)
    data = json.loads(raw.decode())

    vault = Vault(vault_name, password)
    vault.data = data
    vault.save()
    return vault


def merge_vault(
    source: Vault,
    target: Vault,
    conflict: str = "keep_target",
) -> dict:
    """Merge variables from source into target vault.

    conflict: 'keep_target' | 'keep_source'
    Returns a dict of keys that had conflicts.
    """
    conflicts = {}
    for key, value in source.data.items():
        if key in target.data:
            conflicts[key] = {"source": value, "target": target.data[key]}
            if conflict == "keep_source":
                target.data[key] = value
        else:
            target.data[key] = value
    target.save()
    return conflicts
