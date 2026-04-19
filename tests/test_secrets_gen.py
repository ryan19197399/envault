"""Tests for envault.secrets_gen."""
import pytest
from envault.secrets_gen import (
    generate_password,
    generate_token,
    generate_hex,
    generate_and_set,
)


def vault_data():
    return {"vars": {"SECRET_KEY": "old", "API_TOKEN": "old"}}


def test_generate_password_default_length():
    pw = generate_password()
    assert len(pw) == 32


def test_generate_password_custom_length():
    pw = generate_password(length=16)
    assert len(pw) == 16


def test_generate_password_invalid_length():
    with pytest.raises(ValueError):
        generate_password(length=0)


def test_generate_password_uses_alphabet():
    pw = generate_password(length=100, alphabet="abc")
    assert all(c in "abc" for c in pw)


def test_generate_token_returns_string():
    tok = generate_token()
    assert isinstance(tok, str)
    assert len(tok) > 0


def test_generate_token_invalid_bytes():
    with pytest.raises(ValueError):
        generate_token(nbytes=0)


def test_generate_hex_returns_hex_string():
    h = generate_hex(nbytes=16)
    assert len(h) == 32
    int(h, 16)  # should not raise


def test_generate_hex_invalid_bytes():
    with pytest.raises(ValueError):
        generate_hex(nbytes=0)


def test_generate_and_set_updates_vault():
    data = vault_data()
    value = generate_and_set(data, "SECRET_KEY", mode="password", length=20)
    assert data["vars"]["SECRET_KEY"] == value
    assert len(value) == 20


def test_generate_and_set_token_mode():
    data = vault_data()
    value = generate_and_set(data, "API_TOKEN", mode="token", nbytes=16)
    assert data["vars"]["API_TOKEN"] == value


def test_generate_and_set_missing_key_raises():
    data = vault_data()
    with pytest.raises(KeyError):
        generate_and_set(data, "NONEXISTENT", mode="password")


def test_generate_and_set_invalid_mode_raises():
    data = vault_data()
    with pytest.raises(ValueError):
        generate_and_set(data, "SECRET_KEY", mode="uuid")


def test_passwords_are_unique():
    passwords = {generate_password() for _ in range(10)}
    assert len(passwords) == 10
