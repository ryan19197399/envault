"""Tests for envault.fmt formatting utilities."""
import json
import pytest
from envault.fmt import format_table, format_json, format_csv, format_output


@pytest.fixture
def data():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "API_KEY": "secret"}


def test_format_table_basic(data):
    out = format_table(data)
    assert "DB_HOST" in out
    assert "localhost" in out
    assert "API_KEY" in out


def test_format_table_empty():
    assert format_table({}) == "(no variables)"


def test_format_table_with_tags(data):
    tags = {"DB_HOST": ["db", "prod"], "API_KEY": ["auth"]}
    out = format_table(data, tags=tags)
    assert "db, prod" in out
    assert "TAGS" in out


def test_format_table_with_notes(data):
    notes = {"DB_HOST": "primary host"}
    out = format_table(data, notes=notes)
    assert "primary host" in out
    assert "NOTE" in out


def test_format_json_valid(data):
    out = format_json(data)
    parsed = json.loads(out)
    assert parsed["DB_HOST"] == "localhost"
    assert parsed["DB_PORT"] == "5432"


def test_format_json_sorted(data):
    out = format_json(data)
    keys = list(json.loads(out).keys())
    assert keys == sorted(keys)


def test_format_csv_header(data):
    out = format_csv(data)
    assert out.startswith("key,value")


def test_format_csv_contains_entries(data):
    out = format_csv(data)
    assert '"DB_HOST","localhost"' in out
    assert '"API_KEY","secret"' in out


def test_format_csv_escapes_quotes():
    out = format_csv({"KEY": 'val"ue'})
    assert '"val""ue"' in out


def test_format_output_dispatches_json(data):
    out = format_output(data, fmt="json")
    assert json.loads(out)["DB_HOST"] == "localhost"


def test_format_output_dispatches_csv(data):
    out = format_output(data, fmt="csv")
    assert "key,value" in out


def test_format_output_default_table(data):
    out = format_output(data)
    assert "KEY" in out
    assert "VALUE" in out
