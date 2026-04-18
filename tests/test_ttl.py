"""Tests for envault/ttl.py"""

import pytest
from datetime import datetime, timedelta
from envault.ttl import set_ttl, remove_ttl, get_ttl, is_expired, purge_expired, TTL_KEY


@pytest.fixture
def vault_data():
    return {"vars": {"API_KEY": "secret", "DB_PASS": "pass123"}}


def test_set_ttl_creates_ttl_key(vault_data):
    set_ttl(vault_data, "API_KEY", 300)
    assert TTL_KEY in vault_data
    assert "API_KEY" in vault_data[TTL_KEY]


def test_set_ttl_stores_future_expiry(vault_data):
    before = datetime.utcnow()
    set_ttl(vault_data, "API_KEY", 60)
    expiry = datetime.fromisoformat(vault_data[TTL_KEY]["API_KEY"])
    assert expiry > before
    assert expiry <= datetime.utcnow() + timedelta(seconds=61)


def test_get_ttl_returns_expiry(vault_data):
    set_ttl(vault_data, "API_KEY", 100)
    result = get_ttl(vault_data, "API_KEY")
    assert result is not None


def test_get_ttl_missing_key_returns_none(vault_data):
    assert get_ttl(vault_data, "MISSING") is None


def test_remove_ttl_returns_true(vault_data):
    set_ttl(vault_data, "API_KEY", 100)
    assert remove_ttl(vault_data, "API_KEY") is True
    assert get_ttl(vault_data, "API_KEY") is None


def test_remove_ttl_missing_returns_false(vault_data):
    assert remove_ttl(vault_data, "NOPE") is False


def test_is_expired_future_not_expired(vault_data):
    set_ttl(vault_data, "API_KEY", 3600)
    assert is_expired(vault_data, "API_KEY") is False


def test_is_expired_past_is_expired(vault_data):
    past = (datetime.utcnow() - timedelta(seconds=1)).isoformat()
    vault_data[TTL_KEY] = {"API_KEY": past}
    assert is_expired(vault_data, "API_KEY") is True


def test_is_expired_no_ttl_returns_false(vault_data):
    assert is_expired(vault_data, "API_KEY") is False


def test_purge_expired_removes_keys(vault_data):
    past = (datetime.utcnow() - timedelta(seconds=5)).isoformat()
    vault_data[TTL_KEY] = {"API_KEY": past}
    purged = purge_expired(vault_data)
    assert "API_KEY" in purged
    assert "API_KEY" not in vault_data["vars"]
    assert "API_KEY" not in vault_data[TTL_KEY]


def test_purge_expired_keeps_valid_keys(vault_data):
    set_ttl(vault_data, "DB_PASS", 3600)
    past = (datetime.utcnow() - timedelta(seconds=5)).isoformat()
    vault_data[TTL_KEY]["API_KEY"] = past
    purged = purge_expired(vault_data)
    assert purged == ["API_KEY"]
    assert "DB_PASS" in vault_data["vars"]
