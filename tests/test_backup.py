import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from envault.backup import create_backup, list_backups, restore_backup, delete_backup, prune_backups


@pytest.fixture
def vault_dir(tmp_path, monkeypatch):
    def fake_vault_path(name):
        p = tmp_path / "vaults" / f"{name}.vault"
        p.parent.mkdir(parents=True, exist_ok=True)
        return p
    monkeypatch.setattr("envault.backup._vault_path", fake_vault_path)
    return tmp_path


def _make_vault(vault_dir, name="default"):
    p = vault_dir / "vaults" / f"{name}.vault"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"encrypted")
    return p


def test_create_backup_creates_file(vault_dir):
    _make_vault(vault_dir)
    path = create_backup("default")
    assert path.exists()
    assert path.suffix == ".bak"


def test_create_backup_missing_vault_raises(vault_dir):
    with pytest.raises(FileNotFoundError):
        create_backup("ghost")


def test_list_backups_empty(vault_dir):
    _make_vault(vault_dir)
    assert list_backups("default") == []


def test_list_backups_returns_sorted(vault_dir):
    _make_vault(vault_dir)
    b1 = create_backup("default")
    b2 = create_backup("default")
    backups = list_backups("default")
    assert len(backups) == 2
    assert backups[0].name <= backups[1].name


def test_restore_backup_overwrites_vault(vault_dir):
    vp = _make_vault(vault_dir)
    bak = create_backup("default")
    vp.write_bytes(b"changed")
    restore_backup("default", bak)
    assert vp.read_bytes() == b"encrypted"


def test_restore_missing_backup_raises(vault_dir):
    _make_vault(vault_dir)
    with pytest.raises(FileNotFoundError):
        restore_backup("default", Path("/nonexistent/file.bak"))


def test_delete_backup(vault_dir):
    _make_vault(vault_dir)
    bak = create_backup("default")
    assert delete_backup(bak) is True
    assert not bak.exists()


def test_delete_backup_missing_returns_false(vault_dir):
    assert delete_backup(Path("/no/such/file.bak")) is False


def test_prune_keeps_n_most_recent(vault_dir):
    _make_vault(vault_dir)
    for _ in range(7):
        create_backup("default")
    deleted = prune_backups("default", keep=3)
    assert len(deleted) == 4
    assert len(list_backups("default")) == 3
