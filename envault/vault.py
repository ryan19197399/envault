"""High-level Vault class for managing environment variable collections."""

from pathlib import Path
from envault.storage import save_vault, load_vault, vault_exists, DEFAULT_VAULT_DIR


class Vault:
    def __init__(self, name: str, password: str, vault_dir: Path = DEFAULT_VAULT_DIR):
        self.name = name
        self.password = password
        self.vault_dir = vault_dir
        self._secrets: dict = {}

    def load(self) -> "Vault":
        """Load secrets from encrypted storage."""
        self._secrets = load_vault(self.name, self.password, self.vault_dir)
        return self

    def save(self) -> Path:
        """Persist current secrets to encrypted storage."""
        return save_vault(self.name, self._secrets, self.password, self.vault_dir)

    def set(self, key: str, value: str) -> None:
        self._secrets[key] = value

    def get(self, key: str) -> str | None:
        return self._secrets.get(key)

    def delete(self, key: str) -> bool:
        if key in self._secrets:
            del self._secrets[key]
            return True
        return False

    def all(self) -> dict:
        return dict(self._secrets)

    def exists(self) -> bool:
        return vault_exists(self.name, self.vault_dir)

    @classmethod
    def create(cls, name: str, password: str, vault_dir: Path = DEFAULT_VAULT_DIR) -> "Vault":
        """Create a new empty vault and persist it."""
        v = cls(name, password, vault_dir)
        v.save()
        return v

    def __repr__(self) -> str:
        return f"<Vault name={self.name!r} keys={list(self._secrets.keys())}>"
