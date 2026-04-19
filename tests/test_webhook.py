"""Tests for envault/webhook.py."""
import pytest
from unittest.mock import patch, MagicMock
from envault.webhook import set_webhook, remove_webhook, list_webhooks, fire_webhook


@pytest.fixture
def vault_data():
    return {"vars": {"KEY": "val"}}


def test_set_webhook_creates_key(vault_data):
    set_webhook(vault_data, "https://example.com/hook")
    assert "_webhooks" in vault_data


def test_set_webhook_stores_url(vault_data):
    set_webhook(vault_data, "https://example.com/hook")
    assert "https://example.com/hook" in vault_data["_webhooks"]


def test_set_webhook_default_events(vault_data):
    set_webhook(vault_data, "https://example.com/hook")
    hook = vault_data["_webhooks"]["https://example.com/hook"]
    assert hook["events"] == ["*"]


def test_set_webhook_custom_events(vault_data):
    set_webhook(vault_data, "https://example.com/hook", ["set", "delete"])
    hook = vault_data["_webhooks"]["https://example.com/hook"]
    assert "set" in hook["events"]
    assert "delete" in hook["events"]


def test_remove_webhook_returns_true(vault_data):
    set_webhook(vault_data, "https://example.com/hook")
    result = remove_webhook(vault_data, "https://example.com/hook")
    assert result is True


def test_remove_webhook_missing_returns_false(vault_data):
    result = remove_webhook(vault_data, "https://missing.com")
    assert result is False


def test_list_webhooks_empty(vault_data):
    assert list_webhooks(vault_data) == []


def test_list_webhooks_returns_all(vault_data):
    set_webhook(vault_data, "https://a.com")
    set_webhook(vault_data, "https://b.com")
    hooks = list_webhooks(vault_data)
    assert len(hooks) == 2


def test_fire_webhook_calls_url(vault_data):
    set_webhook(vault_data, "https://example.com/hook")
    mock_resp = MagicMock()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
        results = fire_webhook(vault_data, "set", {"key": "X"})
    assert len(results) == 1
    assert results[0][0] == "https://example.com/hook"
    assert results[0][1] is True


def test_fire_webhook_filtered_event(vault_data):
    set_webhook(vault_data, "https://example.com/hook", ["delete"])
    results = fire_webhook(vault_data, "set", {})
    assert results == []


def test_fire_webhook_failure_returns_false(vault_data):
    set_webhook(vault_data, "https://example.com/hook")
    with patch("urllib.request.urlopen", side_effect=Exception("timeout")):
        results = fire_webhook(vault_data, "set", {})
    assert results[0][1] is False
