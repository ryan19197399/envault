"""Access control: per-key read/write permissions within a vault."""

ACCESS_KEY = "_access"
READ = "read"
WRITE = "write"
VALID_PERMS = {READ, WRITE}


def set_permission(vault_data: dict, key: str, perm: str, principal: str) -> None:
    """Grant a principal (e.g. profile/user label) a permission on a key."""
    if perm not in VALID_PERMS:
        raise ValueError(f"Invalid permission '{perm}'. Choose from {VALID_PERMS}.")
    access = vault_data.setdefault(ACCESS_KEY, {})
    entry = access.setdefault(key, {READ: [], WRITE: []})
    if principal not in entry[perm]:
        entry[perm].append(principal)


def remove_permission(vault_data: dict, key: str, perm: str, principal: str) -> bool:
    """Revoke a principal's permission on a key. Returns True if removed."""
    access = vault_data.get(ACCESS_KEY, {})
    entry = access.get(key, {})
    lst = entry.get(perm, [])
    if principal in lst:
        lst.remove(principal)
        return True
    return False


def get_permissions(vault_data: dict, key: str) -> dict:
    """Return permission dict for a key, or empty structure if none set."""
    return vault_data.get(ACCESS_KEY, {}).get(key, {READ: [], WRITE: []})


def has_permission(vault_data: dict, key: str, perm: str, principal: str) -> bool:
    """Check if a principal has a given permission on a key."""
    entry = get_permissions(vault_data, key)
    return principal in entry.get(perm, [])


def list_access(vault_data: dict) -> dict:
    """Return the full access control map."""
    return dict(vault_data.get(ACCESS_KEY, {}))


def clear_permissions(vault_data: dict, key: str) -> bool:
    """Remove all permissions for a key. Returns True if anything was cleared."""
    access = vault_data.get(ACCESS_KEY, {})
    if key in access:
        del access[key]
        return True
    return False
