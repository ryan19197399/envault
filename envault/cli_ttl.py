"""CLI commands for managing variable TTLs."""

import click
from envault.vault import Vault
from envault.ttl import set_ttl, remove_ttl, get_ttl, purge_expired


@click.group()
def ttl():
    """Manage TTL (expiry) for vault variables."""


@ttl.command("set")
@click.argument("vault_name")
@click.argument("key")
@click.argument("seconds", type=int)
@click.password_option(prompt="Vault password")
def set_cmd(vault_name, key, seconds, password):
    """Set TTL in SECONDS for KEY in VAULT_NAME."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    if key not in v.data.get("vars", {}):
        click.echo(f"Key '{key}' not found in vault.", err=True)
        raise SystemExit(1)
    set_ttl(v.data, key, seconds)
    v.save()
    click.echo(f"TTL of {seconds}s set for '{key}'.")


@ttl.command("remove")
@click.argument("vault_name")
@click.argument("key")
@click.password_option(prompt="Vault password")
def remove_cmd(vault_name, key, password):
    """Remove TTL for KEY in VAULT_NAME."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    removed = remove_ttl(v.data, key)
    if removed:
        v.save()
        click.echo(f"TTL removed for '{key}'.")
    else:
        click.echo(f"No TTL set for '{key}'.")


@ttl.command("show")
@click.argument("vault_name")
@click.argument("key")
@click.password_option(prompt="Vault password")
def show_cmd(vault_name, key, password):
    """Show TTL expiry for KEY in VAULT_NAME."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    expiry = get_ttl(v.data, key)
    if expiry:
        click.echo(f"'{key}' expires at {expiry} UTC")
    else:
        click.echo(f"No TTL set for '{key}'.")


@ttl.command("purge")
@click.argument("vault_name")
@click.password_option(prompt="Vault password")
def purge_cmd(vault_name, password):
    """Purge all expired keys from VAULT_NAME."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    purged = purge_expired(v.data)
    if purged:
        v.save()
        click.echo(f"Purged {len(purged)} expired key(s): {', '.join(purged)}")
    else:
        click.echo("No expired keys found.")
