"""Tests for envault.sync module."""

import pytest
from pathlib import Path

from envault.sync import export_vault, import_vault, merge_vault
from envault.vault import Vault
from envault.storage import _vault_path


PASSWORD = "sync-secret"


@pytest.fixture(autouse=True)
def tmp_vault_dir(tmp_path, monkeypatch):
    import envault.storage as storage
    monkeypatch.setattr(storage, "VAULT_DIR", tmp_path)
    return tmp_path


@pytest.fixture
def sample_vault():
    v = Vault("myproject", PASSWORD)
    v.set("API_KEY", "abc123")
    v.set("DEBUG", "true")
    return v


def test_export_creates_file(sample_vault, tmp_path):
    out = tmp_path / "myproject.vault"
    export_vault(sample_vault, PASSWORD, out)
    assert out.exists()
    assert out.stat().st_size > 0


def test_export_import_roundtrip(sample_vault, tmp_path):
    out = tmp_path / "export.vault"
    export_vault(sample_vault, PASSWORD, out)

    imported = import_vault(out, PASSWORD, "imported_project")
    assert imported.get("API_KEY") == "abc123"
    assert imported.get("DEBUG") == "true"


def test_import_wrong_password_raises(sample_vault, tmp_path):
    from cryptography.fernet import InvalidToken
    out = tmp_path / "export.vault"
    export_vault(sample_vault, PASSWORD, out)
    with pytest.raises(InvalidToken):
        import_vault(out, "wrong-password", "other_project")


def test_import_existing_vault_raises(sample_vault, tmp_path):
    out = tmp_path / "export.vault"
    export_vault(sample_vault, PASSWORD, out)
    import_vault(out, PASSWORD, "copy_project")
    with pytest.raises(FileExistsError):
        import_vault(out, PASSWORD, "copy_project")


def test_import_existing_vault_overwrite(sample_vault, tmp_path):
    out = tmp_path / "export.vault"
    export_vault(sample_vault, PASSWORD, out)
    import_vault(out, PASSWORD, "copy_project")
    imported = import_vault(out, PASSWORD, "copy_project", overwrite=True)
    assert imported.get("API_KEY") == "abc123"


def test_merge_no_conflicts():
    src = Vault("src", PASSWORD)
    src.set("NEW_VAR", "hello")

    tgt = Vault("tgt", PASSWORD)
    tgt.set("EXISTING", "world")

    conflicts = merge_vault(src, tgt)
    assert conflicts == {}
    assert tgt.get("NEW_VAR") == "hello"
    assert tgt.get("EXISTING") == "world"


def test_merge_conflict_keep_target():
    src = Vault("src", PASSWORD)
    src.set("KEY", "from_source")

    tgt = Vault("tgt", PASSWORD)
    tgt.set("KEY", "from_target")

    conflicts = merge_vault(src, tgt, conflict="keep_target")
    assert "KEY" in conflicts
    assert tgt.get("KEY") == "from_target"


def test_merge_conflict_keep_source():
    src = Vault("src", PASSWORD)
    src.set("KEY", "from_source")

    tgt = Vault("tgt", PASSWORD)
    tgt.set("KEY", "from_target")

    conflicts = merge_vault(src, tgt, conflict="keep_source")
    assert "KEY" in conflicts
    assert tgt.get("KEY") == "from_source"
