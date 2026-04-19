"""Profile management: named sets of env vars for different environments."""

PROFILES_KEY = "__profiles__"


def save_profile(vault_data: dict, profile_name: str, keys: list[str]) -> dict:
    """Save a named profile containing a list of variable keys."""
    profiles = vault_data.setdefault(PROFILES_KEY, {})
    profiles[profile_name] = list(set(keys))
    return vault_data


def delete_profile(vault_data: dict, profile_name: str) -> bool:
    """Delete a profile. Returns True if it existed."""
    profiles = vault_data.get(PROFILES_KEY, {})
    if profile_name in profiles:
        del profiles[profile_name]
        return True
    return False


def get_profile(vault_data: dict, profile_name: str) -> list[str] | None:
    """Return keys in a profile, or None if not found."""
    return vault_data.get(PROFILES_KEY, {}).get(profile_name)


def list_profiles(vault_data: dict) -> list[str]:
    """Return all profile names."""
    return list(vault_data.get(PROFILES_KEY, {}).keys())


def apply_profile(vault_data: dict, profile_name: str) -> dict | None:
    """Return a dict of key/value pairs for all keys in the profile."""
    keys = get_profile(vault_data, profile_name)
    if keys is None:
        return None
    vars_ = vault_data.get("vars", {})
    return {k: vars_[k] for k in keys if k in vars_}


def rename_profile(vault_data: dict, old_name: str, new_name: str) -> bool:
    """Rename a profile. Returns True if successful, False if old_name not found."""
    profiles = vault_data.get(PROFILES_KEY, {})
    if old_name not in profiles:
        return False
    profiles[new_name] = profiles.pop(old_name)
    return True
