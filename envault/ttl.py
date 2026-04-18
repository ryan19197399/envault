"""TTL (time-to-live) support for vault variables."""

from datetime import datetime, timedelta
from typing import Optional

TTL_KEY = "__ttl__"


def set_ttl(vault_data: dict, key: str, seconds: int) -> None:
    """Set expiry time for a key."""
    if TTL_KEY not in vault_data:
        vault_data[TTL_KEY] = {}
    expires_at = (datetime.utcnow() + timedelta(seconds=seconds)).isoformat()
    vault_data[TTL_KEY][key] = expires_at


def remove_ttl(vault_data: dict, key: str) -> bool:
    """Remove TTL for a key. Returns True if removed."""
    ttls = vault_data.get(TTL_KEY, {})
    if key in ttls:
        del ttls[key]
        return True
    return False


def get_ttl(vault_data: dict, key: str) -> Optional[str]:
    """Return ISO expiry string for key, or None."""
    return vault_data.get(TTL_KEY, {}).get(key)


def is_expired(vault_data: dict, key: str) -> bool:
    """Return True if the key has a TTL that has passed."""
    expiry = get_ttl(vault_data, key)
    if expiry is None:
        return False
    return datetime.utcnow() > datetime.fromisoformat(expiry)


def purge_expired(vault_data: dict) -> list:
    """Remove all expired keys from vault_data. Returns list of purged keys."""
    purged = []
    ttls = vault_data.get(TTL_KEY, {})
    expired_keys = [k for k in ttls if is_expired(vault_data, k)]
    for key in expired_keys:
        vault_data.get("vars", {}).pop(key, None)
        del ttls[key]
        purged.append(key)
    return purged
