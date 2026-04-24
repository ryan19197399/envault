"""Tests for envault/chain.py"""
import pytest
from envault.chain import set_chain, remove_chain, get_chain, list_chains, run_chain


@pytest.fixture
def vault_data():
    return {"vars": {"DB_HOST": "localhost", "DB_PORT": "5432", "API_KEY": "secret"}}


def test_set_chain_creates_key(vault_data):
    set_chain(vault_data, "db_chain", ["DB_HOST", "DB_PORT"])
    assert "_chains" in vault_data
    assert "db_chain" in vault_data["_chains"]


def test_set_chain_stores_steps(vault_data):
    set_chain(vault_data, "db_chain", ["DB_HOST", "DB_PORT"])
    assert vault_data["_chains"]["db_chain"]["steps"] == ["DB_HOST", "DB_PORT"]


def test_set_chain_empty_steps_raises(vault_data):
    with pytest.raises(ValueError):
        set_chain(vault_data, "bad", [])


def test_set_chain_overwrites_existing(vault_data):
    set_chain(vault_data, "chain", ["DB_HOST"])
    set_chain(vault_data, "chain", ["DB_PORT"])
    assert vault_data["_chains"]["chain"]["steps"] == ["DB_PORT"]


def test_get_chain_returns_steps(vault_data):
    set_chain(vault_data, "db_chain", ["DB_HOST", "DB_PORT"])
    steps = get_chain(vault_data, "db_chain")
    assert steps == ["DB_HOST", "DB_PORT"]


def test_get_chain_missing_returns_none(vault_data):
    assert get_chain(vault_data, "nonexistent") is None


def test_remove_chain_returns_true(vault_data):
    set_chain(vault_data, "chain", ["DB_HOST"])
    assert remove_chain(vault_data, "chain") is True
    assert get_chain(vault_data, "chain") is None


def test_remove_chain_missing_returns_false(vault_data):
    assert remove_chain(vault_data, "ghost") is False


def test_list_chains_empty(vault_data):
    assert list_chains(vault_data) == []


def test_list_chains_returns_names(vault_data):
    set_chain(vault_data, "a", ["DB_HOST"])
    set_chain(vault_data, "b", ["API_KEY"])
    names = list_chains(vault_data)
    assert set(names) == {"a", "b"}


def test_run_chain_returns_values(vault_data):
    set_chain(vault_data, "db_chain", ["DB_HOST", "DB_PORT"])
    results = run_chain(vault_data, "db_chain")
    assert results == ["localhost", "5432"]


def test_run_chain_missing_chain_raises(vault_data):
    with pytest.raises(KeyError, match="not found"):
        run_chain(vault_data, "ghost")


def test_run_chain_missing_key_raises(vault_data):
    set_chain(vault_data, "bad_chain", ["MISSING_KEY"])
    with pytest.raises(KeyError, match="MISSING_KEY"):
        run_chain(vault_data, "bad_chain")
