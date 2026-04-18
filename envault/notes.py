"""Per-key notes/annotations for vault entries."""

NOTES_KEY = "__notes__"


def set_note(vault_data: dict, key: str, note: str) -> dict:
    """Set a note for a given key."""
    if NOTES_KEY not in vault_data:
        vault_data[NOTES_KEY] = {}
    vault_data[NOTES_KEY][key] = note
    return vault_data


def get_note(vault_data: dict, key: str) -> str | None:
    """Get the note for a given key, or None if not set."""
    return vault_data.get(NOTES_KEY, {}).get(key)


def remove_note(vault_data: dict, key: str) -> bool:
    """Remove the note for a given key. Returns True if removed, False if not found."""
    notes = vault_data.get(NOTES_KEY, {})
    if key in notes:
        del notes[key]
        return True
    return False


def list_notes(vault_data: dict) -> dict:
    """Return all key->note mappings."""
    return dict(vault_data.get(NOTES_KEY, {}))


def clear_notes(vault_data: dict) -> dict:
    """Remove all notes from vault data."""
    vault_data.pop(NOTES_KEY, None)
    return vault_data
