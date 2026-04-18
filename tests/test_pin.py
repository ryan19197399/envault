"""Tests for envault/pin.py"""

import time
import pytest
from envault.pin import set_pin, verify_pin, remove_pin, pin_expires_at, is_pin_expired


@pytest.fixture
def vault_data():
    return {"vars": {"KEY": "value"}, "_meta": {}}


def test_set_pin_creates_meta_pin(vault_data):
    set_pin(vault_data, "1234")
    assert "pin" in vault_data["_meta"]


def test_set_pin_stores_hash(vault_data):
    set_pin(vault_data, "1234")
    import hashlib
    expected = hashlib.sha256(b"1234").hexdigest()
    assert vault_data["_meta"]["pin"]["hash"] == expected


def test_set_pin_stores_expiry(vault_data):
    before = time.time()
    set_pin(vault_data, "1234", ttl_seconds=60)
    after = time.time()
    expires = vault_data["_meta"]["pin"]["expires_at"]
    assert before + 60 <= expires <= after + 60


def test_verify_pin_correct(vault_data):
    set_pin(vault_data, "secret", ttl_seconds=60)
    assert verify_pin(vault_data, "secret") is True


def test_verify_pin_wrong(vault_data):
    set_pin(vault_data, "secret", ttl_seconds=60)
    assert verify_pin(vault_data, "wrong") is False


def test_verify_pin_expired(vault_data):
    set_pin(vault_data, "secret", ttl_seconds=-1)
    assert verify_pin(vault_data, "secret") is False


def test_verify_pin_no_pin(vault_data):
    assert verify_pin(vault_data, "anything") is False


def test_remove_pin(vault_data):
    set_pin(vault_data, "1234")
    remove_pin(vault_data)
    assert "pin" not in vault_data.get("_meta", {})


def test_pin_expires_at_none_when_not_set(vault_data):
    assert pin_expires_at(vault_data) is None


def test_is_pin_expired_true_when_not_set(vault_data):
    assert is_pin_expired(vault_data) is True


def test_is_pin_expired_false_when_active(vault_data):
    set_pin(vault_data, "1234", ttl_seconds=3600)
    assert is_pin_expired(vault_data) is False


def test_is_pin_expired_true_when_expired(vault_data):
    set_pin(vault_data, "1234", ttl_seconds=-10)
    assert is_pin_expired(vault_data) is True
