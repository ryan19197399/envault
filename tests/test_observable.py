"""Tests for envault/observable.py."""

import pytest
from envault import observable as obs


@pytest.fixture
def vault_data():
    return {
        "vars": {
            "API_KEY": "abc123",
            "BACKUP_KEY": "old",
            "DB_PASS": "secret",
        }
    }


def test_set_observer_creates_key(vault_data):
    obs.set_observer(vault_data, "API_KEY", "log")
    assert "_observables" in vault_data
    assert "API_KEY" in vault_data["_observables"]


def test_set_observer_stores_action(vault_data):
    obs.set_observer(vault_data, "API_KEY", "notify")
    entry = vault_data["_observables"]["API_KEY"]
    assert entry["action"] == "notify"


def test_set_observer_copy_stores_target(vault_data):
    obs.set_observer(vault_data, "API_KEY", "copy", target="BACKUP_KEY")
    entry = vault_data["_observables"]["API_KEY"]
    assert entry["action"] == "copy"
    assert entry["target"] == "BACKUP_KEY"


def test_set_observer_invalid_action_raises(vault_data):
    with pytest.raises(ValueError, match="Invalid action"):
        obs.set_observer(vault_data, "API_KEY", "explode")


def test_set_observer_missing_key_raises(vault_data):
    with pytest.raises(KeyError, match="MISSING"):
        obs.set_observer(vault_data, "MISSING", "log")


def test_set_observer_copy_without_target_raises(vault_data):
    with pytest.raises(ValueError, match="target"):
        obs.set_observer(vault_data, "API_KEY", "copy")


def test_set_observer_copy_missing_target_raises(vault_data):
    with pytest.raises(KeyError, match="NONEXISTENT"):
        obs.set_observer(vault_data, "API_KEY", "copy", target="NONEXISTENT")


def test_remove_observer_returns_true(vault_data):
    obs.set_observer(vault_data, "API_KEY", "log")
    result = obs.remove_observer(vault_data, "API_KEY")
    assert result is True
    assert "API_KEY" not in vault_data["_observables"]


def test_remove_observer_missing_returns_false(vault_data):
    result = obs.remove_observer(vault_data, "API_KEY")
    assert result is False


def test_get_observer_returns_entry(vault_data):
    obs.set_observer(vault_data, "DB_PASS", "notify")
    entry = obs.get_observer(vault_data, "DB_PASS")
    assert entry is not None
    assert entry["action"] == "notify"


def test_get_observer_missing_returns_none(vault_data):
    assert obs.get_observer(vault_data, "API_KEY") is None


def test_list_observers_returns_all(vault_data):
    obs.set_observer(vault_data, "API_KEY", "log")
    obs.set_observer(vault_data, "DB_PASS", "notify")
    entries = obs.list_observers(vault_data)
    keys = [e["key"] for e in entries]
    assert "API_KEY" in keys
    assert "DB_PASS" in keys


def test_list_observers_empty(vault_data):
    assert obs.list_observers(vault_data) == []


def test_fire_observers_log(vault_data):
    obs.set_observer(vault_data, "API_KEY", "log")
    logs = obs.fire_observers(vault_data, "API_KEY", "old", "new")
    assert len(logs) == 1
    assert "API_KEY" in logs[0]
    assert "old" in logs[0]
    assert "new" in logs[0]


def test_fire_observers_copy_updates_target(vault_data):
    obs.set_observer(vault_data, "API_KEY", "copy", target="BACKUP_KEY")
    obs.fire_observers(vault_data, "API_KEY", "abc123", "xyz789")
    assert vault_data["vars"]["BACKUP_KEY"] == "xyz789"


def test_fire_observers_notify(vault_data):
    obs.set_observer(vault_data, "API_KEY", "notify")
    logs = obs.fire_observers(vault_data, "API_KEY", "old", "new")
    assert any("NOTIFY" in l for l in logs)


def test_fire_observers_no_observer_returns_empty(vault_data):
    logs = obs.fire_observers(vault_data, "API_KEY", "old", "new")
    assert logs == []
