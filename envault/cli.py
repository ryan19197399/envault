"""Main CLI entry point for envault."""

import click
from envault.vault import Vault
from envault.storage import list_vaults
from envault.cli_sync import sync
from envault.cli_audit import audit
from envault.cli_tags import tag
from envault.cli_profiles import profile
from envault.cli_history import history


@click.group()
def cli():
    """envault — encrypted environment variable manager."""
    pass


@cli.command()
@click.argument("vault_name")
@click.password_option()
def init(vault_name, password):
    """Initialize a new vault."""
    vault = Vault(vault_name, password)
    if vault.exists():
        click.echo(f"Vault '{vault_name}' already exists.", err=True)
        raise SystemExit(1)
    vault.save()
    click.echo(f"Vault '{vault_name}' created.")


@cli.command("set")
@click.argument("vault_name")
@click.argument("key")
@click.argument("value")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def set_var(vault_name, key, value, password):
    """Set a variable in a vault."""
    vault = Vault(vault_name, password)
    vault.load()
    old = vault.get(key)
    vault.set(key, value)
    from envault.history import record_change
    record_change(vault.data, key, "set" if old is None else "update",
                  old_value=old, new_value=value)
    vault.save()
    click.echo(f"Set {key}.")


@cli.command("get")
@click.argument("vault_name")
@click.argument("key")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def get_var(vault_name, key, password):
    """Get a variable from a vault."""
    vault = Vault(vault_name, password)
    vault.load()
    value = vault.get(key)
    if value is None:
        click.echo(f"Key '{key}' not found.", err=True)
        raise SystemExit(1)
    click.echo(value)


@cli.command("list")
@click.argument("vault_name")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def list_vars(vault_name, password):
    """List all variables in a vault."""
    vault = Vault(vault_name, password)
    vault.load()
    keys = vault.list_keys()
    if not keys:
        click.echo("No variables set.")
    for k in keys:
        click.echo(k)


@cli.command("delete")
@click.argument("vault_name")
@click.argument("key")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def delete_var(vault_name, key, password):
    """Delete a variable from a vault."""
    vault = Vault(vault_name, password)
    vault.load()
    old = vault.get(key)
    removed = vault.delete(key)
    if not removed:
        click.echo(f"Key '{key}' not found.", err=True)
        raise SystemExit(1)
    from envault.history import record_change
    record_change(vault.data, key, "delete", old_value=old)
    vault.save()
    click.echo(f"Deleted {key}.")


@cli.command("vaults")
def vaults():
    """List all available vaults."""
    names = list_vaults()
    if not names:
        click.echo("No vaults found.")
    for name in names:
        click.echo(name)


cli.add_command(sync)
cli.add_command(audit)
cli.add_command(tag)
cli.add_command(profile)
cli.add_command(history)
