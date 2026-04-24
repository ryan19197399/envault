"""Tag management for vault variables."""
from typing import Dict, List, Optional

TAGS_KEY = "__tags__"


def set_tag(vault_data: dict, key: str, tag: str) -> None:
    """Assign a tag to a variable key."""
    if TAGS_KEY not in vault_data:
        vault_data[TAGS_KEY] = {}
    tags = vault_data[TAGS_KEY]
    if key not in tags:
        tags[key] = []
    if tag not in tags[key]:
        tags[key].append(tag)


def remove_tag(vault_data: dict, key: str, tag: str) -> bool:
    """Remove a tag from a variable key. Returns True if removed."""
    tags = vault_data.get(TAGS_KEY, {})
    if key in tags and tag in tags[key]:
        tags[key].remove(tag)
        if not tags[key]:
            del tags[key]
        return True
    return False


def get_tags(vault_data: dict, key: str) -> List[str]:
    """Return list of tags for a given key."""
    return vault_data.get(TAGS_KEY, {}).get(key, [])


def list_by_tag(vault_data: dict, tag: str) -> List[str]:
    """Return all keys that have the given tag."""
    tags_map: Dict[str, List[str]] = vault_data.get(TAGS_KEY, {})
    return [key for key, tag_list in tags_map.items() if tag in tag_list]


def all_tags(vault_data: dict) -> List[str]:
    """Return sorted list of all unique tags in the vault."""
    tags_map: Dict[str, List[str]] = vault_data.get(TAGS_KEY, {})
    unique: set = set()
    for tag_list in tags_map.values():
        unique.update(tag_list)
    return sorted(unique)


def rename_tag(vault_data: dict, old_tag: str, new_tag: str) -> int:
    """Rename a tag across all keys in the vault.

    Replaces every occurrence of ``old_tag`` with ``new_tag`` and returns
    the number of keys that were updated.
    """
    tags_map: Dict[str, List[str]] = vault_data.get(TAGS_KEY, {})
    updated = 0
    for key, tag_list in tags_map.items():
        if old_tag in tag_list:
            tag_list.remove(old_tag)
            if new_tag not in tag_list:
                tag_list.append(new_tag)
            updated += 1
    return updated
