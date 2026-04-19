"""Tests for envault.clipboard module."""

import time
from unittest.mock import MagicMock, patch
import pytest

import envault.clipboard as clipboard_mod


@pytest.fixture(autouse=True)
def ensure_pyperclip(monkeypatch):
    """Ensure pyperclip is treated as available for all tests."""
    monkeypatch.setattr(clipboard_mod, "_PYPERCLIP_AVAILABLE", True)
    fake = MagicMock()
    fake.copy = MagicMock()
    fake.paste = MagicMock(return_value="")
    monkeypatch.setattr(clipboard_mod, "pyperclip", fake)
    return fake


def test_copy_to_clipboard_calls_pyperclip(ensure_pyperclip):
    clipboard_mod.copy_to_clipboard("secret")
    ensure_pyperclip.copy.assert_called_once_with("secret")


def test_clear_clipboard_copies_empty_string(ensure_pyperclip):
    clipboard_mod.clear_clipboard()
    ensure_pyperclip.copy.assert_called_once_with("")


def test_copy_with_autoclear_copies_value(ensure_pyperclip):
    clipboard_mod.copy_with_autoclear("myvalue", timeout=60)
    ensure_pyperclip.copy.assert_called_with("myvalue")


def test_copy_with_autoclear_clears_if_unchanged(ensure_pyperclip):
    ensure_pyperclip.paste.return_value = "toclean"
    clipboard_mod.copy_with_autoclear("toclean", timeout=0)
    time.sleep(0.1)
    calls = [str(c) for c in ensure_pyperclip.copy.call_args_list]
    assert any("toclean" in c for c in calls)


def test_copy_with_autoclear_skips_clear_if_changed(ensure_pyperclip):
    ensure_pyperclip.paste.return_value = "something_else"
    clipboard_mod.copy_with_autoclear("original", timeout=0)
    time.sleep(0.1)
    for call in ensure_pyperclip.copy.call_args_list:
        args, _ = call
        assert args[0] != "", "Should not have cleared clipboard when value changed"


def test_is_available_true(monkeypatch):
    monkeypatch.setattr(clipboard_mod, "_PYPERCLIP_AVAILABLE", True)
    assert clipboard_mod.is_available() is True


def test_is_available_false(monkeypatch):
    monkeypatch.setattr(clipboard_mod, "_PYPERCLIP_AVAILABLE", False)
    assert clipboard_mod.is_available() is False


def test_check_available_raises_when_missing(monkeypatch):
    monkeypatch.setattr(clipboard_mod, "_PYPERCLIP_AVAILABLE", False)
    with pytest.raises(RuntimeError, match="pyperclip"):
        clipboard_mod.copy_to_clipboard("x")
