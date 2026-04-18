"""PIN/passphrase shortcut management for vault access."""

import hashlib
import json
import os
import time
from pathlib import Path

_PIN_FILE = ".pin_cache"


def _pin_path(vault_dir: str) -> Path:
    return Path(vault_dir) / _PIN_FILE


def set_pin(vault_data: dict, pin: str, ttl_seconds: int = 3600) -> dict:
    """Store a hashed PIN with expiry in vault metadata."""
    pin_hash = hashlib.sha256(pin.encode()).hexdigest()
    vault_data.setdefault("_meta", {})["pin"] = {
        "hash": pin_hash,
        "expires_at": time.time() + ttl_seconds,
    }
    return vault_data


def verify_pin(vault_data: dict, pin: str) -> bool:
    """Verify PIN against stored hash. Returns False if missing or expired."""
    meta = vault_data.get("_meta", {})
    pin_entry = meta.get("pin")
    if not pin_entry:
        return False
    if time.time() > pin_entry.get("expires_at", 0):
        return False
    pin_hash = hashlib.sha256(pin.encode()).hexdigest()
    return pin_hash == pin_entry["hash"]


def remove_pin(vault_data: dict) -> dict:
    """Remove PIN from vault metadata."""
    vault_data.get("_meta", {}).pop("pin", None)
    return vault_data


def pin_expires_at(vault_data: dict) -> float | None:
    """Return expiry timestamp of PIN, or None if not set."""
    return vault_data.get("_meta", {}).get("pin", {}).get("expires_at")


def is_pin_expired(vault_data: dict) -> bool:
    """Return True if PIN is missing or expired."""
    expires_at = pin_expires_at(vault_data)
    if expires_at is None:
        return True
    return time.time() > expires_at
