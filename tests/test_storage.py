"""Tests for envault.storage vault persistence."""

import pytest
from pathlib import Path
from envault.storage import save_vault, load_vault, vault_exists, list_vaults, delete_vault


@pytest.fixture
def tmp_vault_dir(tmp_path):
    return tmp_path / "vaults"


def test_save_and_load(tmp_vault_dir):
    secrets = {"DB_URL": "postgres://localhost/db", "API_KEY": "xyz"}
    save_vault("myproject", secrets, "pass", tmp_vault_dir)
    loaded = load_vault("myproject", "pass", tmp_vault_dir)
    assert loaded == secrets


def test_vault_exists(tmp_vault_dir):
    assert not vault_exists("missing", tmp_vault_dir)
    save_vault("exists", {}, "pass", tmp_vault_dir)
    assert vault_exists("exists", tmp_vault_dir)


def test_list_vaults(tmp_vault_dir):
    save_vault("alpha", {}, "pass", tmp_vault_dir)
    save_vault("beta", {}, "pass", tmp_vault_dir)
    vaults = list_vaults(tmp_vault_dir)
    assert set(vaults) == {"alpha", "beta"}


def test_delete_vault(tmp_vault_dir):
    save_vault("todelete", {"K": "V"}, "pass", tmp_vault_dir)
    delete_vault("todelete", tmp_vault_dir)
    assert not vault_exists("todelete", tmp_vault_dir)


def test_load_missing_vault_raises(tmp_vault_dir):
    with pytest.raises(FileNotFoundError):
        load_vault("ghost", "pass", tmp_vault_dir)


def test_wrong_password_raises(tmp_vault_dir):
    save_vault("locked", {"X": "1"}, "correct", tmp_vault_dir)
    with pytest.raises(Exception):
        load_vault("locked", "wrong", tmp_vault_dir)
