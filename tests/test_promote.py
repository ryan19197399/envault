"""Tests for envault/promote.py"""

import pytest
from envault.promote import (
    promote_key,
    promote_all,
    next_env,
    get_env_chain,
    set_env_chain,
    ENV_ORDER,
)


@pytest.fixture
def src():
    return {"vars": {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"}}


@pytest.fixture
def dst():
    return {"vars": {"DB_HOST": "prod-db"}}


def test_promote_key_success(src, dst):
    result = promote_key(src, dst, "DB_PORT")
    assert result is True
    assert dst["vars"]["DB_PORT"] == "5432"


def test_promote_key_skips_existing_without_overwrite(src, dst):
    result = promote_key(src, dst, "DB_HOST")
    assert result is False
    assert dst["vars"]["DB_HOST"] == "prod-db"  # unchanged


def test_promote_key_overwrites_when_flag_set(src, dst):
    result = promote_key(src, dst, "DB_HOST", overwrite=True)
    assert result is True
    assert dst["vars"]["DB_HOST"] == "localhost"


def test_promote_key_missing_key_raises(src, dst):
    with pytest.raises(KeyError, match="MISSING"):
        promote_key(src, dst, "MISSING")


def test_promote_all_returns_summary(src, dst):
    summary = promote_all(src, dst)
    assert "DB_PORT" in summary["promoted"]
    assert "SECRET" in summary["promoted"]
    assert "DB_HOST" in summary["skipped"]


def test_promote_all_with_overwrite(src, dst):
    summary = promote_all(src, dst, overwrite=True)
    assert "DB_HOST" in summary["promoted"]
    assert dst["vars"]["DB_HOST"] == "localhost"


def test_promote_all_empty_src():
    src = {"vars": {}}
    dst = {"vars": {"X": "1"}}
    summary = promote_all(src, dst)
    assert summary["promoted"] == []
    assert summary["skipped"] == []


def test_get_env_chain_default():
    vault_data = {}
    assert get_env_chain(vault_data) == ENV_ORDER


def test_set_and_get_env_chain():
    vault_data = {}
    set_env_chain(vault_data, ["alpha", "beta", "gamma"])
    assert get_env_chain(vault_data) == ["alpha", "beta", "gamma"]


def test_next_env_returns_next():
    vault_data = {}
    assert next_env(vault_data, "dev") == "staging"
    assert next_env(vault_data, "staging") == "prod"


def test_next_env_returns_none_at_end():
    vault_data = {}
    assert next_env(vault_data, "prod") is None


def test_next_env_returns_none_for_unknown():
    vault_data = {}
    assert next_env(vault_data, "unknown") is None


def test_next_env_custom_chain():
    vault_data = {}
    set_env_chain(vault_data, ["local", "ci", "live"])
    assert next_env(vault_data, "local") == "ci"
    assert next_env(vault_data, "ci") == "live"
    assert next_env(vault_data, "live") is None
