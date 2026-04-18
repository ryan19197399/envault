"""High-level CLI-friendly dotenv import/export helpers for envault vaults."""
from pathlib import Path
from envault.vault import Vault
from envault.export import to_dotenv, from_dotenv
from envault.audit import log_event


def export_to_dotenv(vault_name: str, password: str, output_path: str) -> int:
    """Export a vault's variables to a .env file. Returns number of keys written."""
    vault = Vault.load(vault_name, password)
    env_text = to_dotenv(vault.data.get("vars", {}))
    Path(output_path).write_text(env_text)
    log_event(vault_name, "export_dotenv", key=output_path)
    return len(vault.data.get("vars", {}))


def import_from_dotenv(vault_name: str, password: str, input_path: str, overwrite: bool = False) -> dict:
    """Import variables from a .env file into a vault.

    Returns a dict with keys 'added', 'skipped', 'overwritten'.
    """
    raw = Path(input_path).read_text()
    parsed = from_dotenv(raw)

    vault = Vault.load(vault_name, password)
    vars_ = vault.data.setdefault("vars", {})

    added, skipped, overwritten = [], [], []
    for key, value in parsed.items():
        if key in vars_:
            if overwrite:
                vars_[key] = value
                overwritten.append(key)
                log_event(vault_name, "import_dotenv_overwrite", key=key)
            else:
                skipped.append(key)
        else:
            vars_[key] = value
            added.append(key)
            log_event(vault_name, "import_dotenv_add", key=key)

    vault.save(password)
    return {"added": added, "skipped": skipped, "overwritten": overwritten}
