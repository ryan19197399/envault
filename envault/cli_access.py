"""CLI commands for managing per-key access permissions."""

import click
from envault.vault import Vault
from envault import access as ac


@click.group()
def access():
    """Manage per-key access permissions."""


@access.command("grant")
@click.argument("vault_name")
@click.argument("key")
@click.argument("perm", type=click.Choice(["read", "write"]))
@click.argument("principal")
@click.password_option(prompt="Vault password")
def grant_cmd(vault_name, key, perm, principal, password):
    """Grant PRINCIPAL read or write permission on KEY."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    if key not in v.data.get("vars", {}):
        click.echo(f"Key '{key}' not found in vault.", err=True)
        raise SystemExit(1)
    ac.set_permission(v.data, key, perm, principal)
    v.save()
    click.echo(f"Granted '{perm}' on '{key}' to '{principal}'.")


@access.command("revoke")
@click.argument("vault_name")
@click.argument("key")
@click.argument("perm", type=click.Choice(["read", "write"]))
@click.argument("principal")
@click.password_option(prompt="Vault password")
def revoke_cmd(vault_name, key, perm, principal, password):
    """Revoke PRINCIPAL's permission on KEY."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    removed = ac.remove_permission(v.data, key, perm, principal)
    if removed:
        v.save()
        click.echo(f"Revoked '{perm}' on '{key}' from '{principal}'.")
    else:
        click.echo("Permission not found.")


@access.command("show")
@click.argument("vault_name")
@click.argument("key")
@click.password_option(prompt="Vault password")
def show_cmd(vault_name, key, password):
    """Show permissions for KEY."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    perms = ac.get_permissions(v.data, key)
    click.echo(f"read:  {', '.join(perms.get('read', [])) or '(none)'}")
    click.echo(f"write: {', '.join(perms.get('write', [])) or '(none)'}")
