"""Tests for envault.crypto encryption/decryption."""

import pytest
from envault.crypto import encrypt, decrypt


def test_encrypt_returns_bytes():
    result = encrypt("hello", "password123")
    assert isinstance(result, bytes)


def test_encrypt_decrypt_roundtrip():
    plaintext = "SECRET_KEY=abc123"
    password = "strongpass"
    token = encrypt(plaintext, password)
    assert decrypt(token, password) == plaintext


def test_different_passwords_fail():
    from cryptography.fernet import InvalidToken
    token = encrypt("data", "correct")
    with pytest.raises(Exception):
        decrypt(token, "wrong")


def test_encrypt_produces_different_ciphertexts():
    """Same plaintext + password should yield different ciphertexts (random salt/IV)."""
    t1 = encrypt("same", "pass")
    t2 = encrypt("same", "pass")
    assert t1 != t2


def test_decrypt_invalid_token_raises():
    with pytest.raises(Exception):
        decrypt(b"notvalidtoken", "pass")
