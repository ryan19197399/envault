import json
import shutil
from datetime import datetime
from pathlib import Path
from envault.storage import _vault_path, load_vault, save_vault


def _backup_dir(vault_name: str) -> Path:
    base = _vault_path(vault_name).parent
    d = base / "backups" / vault_name
    d.mkdir(parents=True, exist_ok=True)
    return d


def create_backup(vault_name: str) -> Path:
    """Create a timestamped backup of the vault file."""
    src = _vault_path(vault_name)
    if not src.exists():
        raise FileNotFoundError(f"Vault '{vault_name}' does not exist.")
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    dest = _backup_dir(vault_name) / f"{vault_name}_{timestamp}.bak"
    shutil.copy2(src, dest)
    return dest


def list_backups(vault_name: str) -> list[Path]:
    """Return sorted list of backup paths (oldest first)."""
    d = _backup_dir(vault_name)
    return sorted(d.glob(f"{vault_name}_*.bak"))


def restore_backup(vault_name: str, backup_path: Path) -> None:
    """Overwrite the vault file with the given backup."""
    if not backup_path.exists():
        raise FileNotFoundError(f"Backup '{backup_path}' not found.")
    dest = _vault_path(vault_name)
    shutil.copy2(backup_path, dest)


def delete_backup(backup_path: Path) -> bool:
    """Delete a specific backup file. Returns True if deleted."""
    if backup_path.exists():
        backup_path.unlink()
        return True
    return False


def prune_backups(vault_name: str, keep: int = 5) -> list[Path]:
    """Remove oldest backups, keeping only `keep` most recent. Returns deleted paths."""
    backups = list_backups(vault_name)
    to_delete = backups[: max(0, len(backups) - keep)]
    for p in to_delete:
        p.unlink()
    return to_delete
