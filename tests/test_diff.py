"""Tests for envault/diff.py"""
import pytest
from envault.diff import diff_vaults, format_diff


@pytest.fixture
def old_vault():
    return {"vars": {"KEY_A": "alpha", "KEY_B": "beta", "KEY_C": "gamma"}}


@pytest.fixture
def new_vault():
    return {"vars": {"KEY_A": "alpha", "KEY_B": "changed", "KEY_D": "delta"}}


def test_diff_added(old_vault, new_vault):
    result = diff_vaults(old_vault, new_vault)
    assert "KEY_D" in result["added"]
    assert result["added"]["KEY_D"] == "delta"


def test_diff_removed(old_vault, new_vault):
    result = diff_vaults(old_vault, new_vault)
    assert "KEY_C" in result["removed"]


def test_diff_changed(old_vault, new_vault):
    result = diff_vaults(old_vault, new_vault)
    assert "KEY_B" in result["changed"]
    assert result["changed"]["KEY_B"]["old"] == "beta"
    assert result["changed"]["KEY_B"]["new"] == "changed"


def test_diff_unchanged(old_vault, new_vault):
    result = diff_vaults(old_vault, new_vault)
    assert "KEY_A" in result["unchanged"]


def test_diff_empty_vaults():
    result = diff_vaults({"vars": {}}, {"vars": {}})
    assert result["added"] == {}
    assert result["removed"] == {}
    assert result["changed"] == {}
    assert result["unchanged"] == {}


def test_format_diff_shows_added(old_vault, new_vault):
    result = diff_vaults(old_vault, new_vault)
    output = format_diff(result)
    assert "+ KEY_D=delta" in output


def test_format_diff_shows_removed(old_vault, new_vault):
    result = diff_vaults(old_vault, new_vault)
    output = format_diff(result)
    assert "- KEY_C=gamma" in output


def test_format_diff_shows_changed(old_vault, new_vault):
    result = diff_vaults(old_vault, new_vault)
    output = format_diff(result)
    assert "~ KEY_B" in output


def test_format_diff_no_diff():
    vault = {"vars": {"X": "1"}}
    result = diff_vaults(vault, vault)
    output = format_diff(result)
    assert output == "(no differences)"


def test_format_diff_show_unchanged(old_vault, new_vault):
    result = diff_vaults(old_vault, new_vault)
    output = format_diff(result, show_unchanged=True)
    assert "KEY_A=alpha" in output
