"""Key rotation: re-encrypt a vault with a new password."""

from envault.storage import load_vault, save_vault
from envault.crypto import derive_key, encrypt, decrypt
from envault.audit import log_event
import json


def rotate_password(vault_name: str, old_password: str, new_password: str) -> None:
    """Re-encrypt vault data with a new password."""
    raw = load_vault(vault_name, old_password)
    save_vault(vault_name, raw, new_password)
    log_event(vault_name, "rotate", key=None)


def rotate_key(vault_name: str, password: str, key: str) -> str:
    """Re-encrypt a specific key's value and return the new ciphertext.

    Useful when rotating secrets at the application level.
    Returns the plaintext value so callers can update downstream systems.
    """
    raw = load_vault(vault_name, password)
    data = json.loads(raw)
    vars_ = data.get("vars", {})
    if key not in vars_:
        raise KeyError(f"Key '{key}' not found in vault '{vault_name}'")
    value = vars_[key]
    # Re-derive and re-encrypt to produce a fresh ciphertext
    derived = derive_key(password)
    new_token = encrypt(value.encode(), derived)
    # We store plaintext in vault; re-save to refresh encryption at rest
    save_vault(vault_name, raw, password)
    log_event(vault_name, "rotate_key", key=key)
    return value
