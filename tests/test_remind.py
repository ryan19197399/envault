import pytest
from datetime import datetime
from envault.remind import (
    set_reminder,
    remove_reminder,
    get_reminder,
    list_due,
    list_reminders,
    REMINDERS_KEY,
)


@pytest.fixture
def vault_data():
    return {"vars": {"API_KEY": "abc123", "DB_PASS": "secret"}}


def test_set_reminder_creates_key(vault_data):
    due = datetime(2030, 1, 1, 12, 0, 0)
    set_reminder(vault_data, "API_KEY", due, "Rotate soon")
    assert REMINDERS_KEY in vault_data


def test_set_reminder_stores_due_and_message(vault_data):
    due = datetime(2030, 6, 15, 9, 0, 0)
    set_reminder(vault_data, "API_KEY", due, "Check expiry")
    entry = vault_data[REMINDERS_KEY]["API_KEY"]
    assert entry["due"] == "2030-06-15T09:00:00"
    assert entry["message"] == "Check expiry"


def test_set_reminder_missing_key_raises(vault_data):
    with pytest.raises(KeyError):
        set_reminder(vault_data, "NONEXISTENT", datetime(2030, 1, 1))


def test_set_reminder_empty_message(vault_data):
    set_reminder(vault_data, "DB_PASS", datetime(2030, 1, 1))
    assert vault_data[REMINDERS_KEY]["DB_PASS"]["message"] == ""


def test_remove_reminder_returns_true(vault_data):
    set_reminder(vault_data, "API_KEY", datetime(2030, 1, 1))
    assert remove_reminder(vault_data, "API_KEY") is True
    assert "API_KEY" not in vault_data[REMINDERS_KEY]


def test_remove_reminder_missing_returns_false(vault_data):
    assert remove_reminder(vault_data, "API_KEY") is False


def test_get_reminder_returns_entry(vault_data):
    due = datetime(2030, 3, 10, 8, 0, 0)
    set_reminder(vault_data, "API_KEY", due, "msg")
    entry = get_reminder(vault_data, "API_KEY")
    assert entry is not None
    assert entry["message"] == "msg"


def test_get_reminder_missing_returns_none(vault_data):
    assert get_reminder(vault_data, "API_KEY") is None


def test_list_due_returns_overdue(vault_data):
    set_reminder(vault_data, "API_KEY", datetime(2000, 1, 1), "old")
    set_reminder(vault_data, "DB_PASS", datetime(2099, 1, 1), "future")
    due = list_due(vault_data, as_of=datetime(2024, 1, 1))
    keys = [k for k, _ in due]
    assert "API_KEY" in keys
    assert "DB_PASS" not in keys


def test_list_due_empty_when_none_overdue(vault_data):
    set_reminder(vault_data, "API_KEY", datetime(2099, 1, 1))
    due = list_due(vault_data, as_of=datetime(2024, 1, 1))
    assert due == []


def test_list_reminders_returns_all(vault_data):
    set_reminder(vault_data, "API_KEY", datetime(2030, 1, 1))
    set_reminder(vault_data, "DB_PASS", datetime(2031, 1, 1))
    all_r = list_reminders(vault_data)
    assert len(all_r) == 2
