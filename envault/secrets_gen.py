"""Generate secure random secret values for vault keys."""
import secrets
import string

DEFAULT_LENGTH = 32
DEFAULT_ALPHABET = string.ascii_letters + string.digits + string.punctuation


def generate_password(length: int = DEFAULT_LENGTH, alphabet: str = DEFAULT_ALPHABET) -> str:
    """Generate a cryptographically secure random password."""
    if length < 1:
        raise ValueError("Length must be at least 1")
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_token(nbytes: int = 32) -> str:
    """Generate a URL-safe base64 token."""
    if nbytes < 1:
        raise ValueError("nbytes must be at least 1")
    return secrets.token_urlsafe(nbytes)


def generate_hex(nbytes: int = 32) -> str:
    """Generate a random hex string."""
    if nbytes < 1:
        raise ValueError("nbytes must be at least 1")
    return secrets.token_hex(nbytes)


def generate_and_set(vault_data: dict, key: str, mode: str = "password", **kwargs) -> str:
    """Generate a secret and store it in vault_data under key."""
    if key not in vault_data.get("vars", {}):
        raise KeyError(f"Key '{key}' not found in vault")
    generators = {
        "password": generate_password,
        "token": generate_token,
        "hex": generate_hex,
    }
    if mode not in generators:
        raise ValueError(f"Unknown mode '{mode}'. Choose from: {list(generators)}")
    value = generators[mode](**kwargs)
    vault_data["vars"][key] = value
    return value
