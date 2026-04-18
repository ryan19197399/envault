"""Main CLI entry point for envault."""

import click
from envault.vault import Vault
from envault.cli_sync import sync
from envault.cli_audit import audit
from envault.cli_tags import tag
from envault.cli_profiles import profile
from envault.cli_history import history
from envault.cli_rotate import rotate
from envault.cli_search import search


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
@click.password_option(confirmation_prompt=False)
def set_var(vault_name, key, value, password):
    """Set a variable in the vault."""
    vault = Vault(vault_name, password)
    if not vault.exists():
        click.echo(f"Vault '{vault_name}' does not exist.", err=True)
        raise SystemExit(1)
    vault.load()
    vault.set(key, value)
    vault.save()
    click.echo(f"Set {key}.")


@cli.command("get")
@click.argument("vault_name")
@click.argument("key")
@click.password_option(confirmation_prompt=False)
def get_var(vault_name, key, password):
    """Get a variable from the vault."""
    vault = Vault(vault_name, password)
    if not vault.exists():
        click.echo(f"Vault '{vault_name}' does not exist.", err=True)
        raise SystemExit(1)
    vault.load()
    value = vault.get(key)
    if value is None:
        click.echo(f"Key '{key}' not found.", err=True)
        raise SystemExit(1)
    click.echo(value)


@cli.command("list")
@click.argument("vault_name")
@click.password_option(confirmation_prompt=False)
def list_vars(vault_name, password):
    """List all variables in the vault."""
    vault = Vault(vault_name, password)
    if not vault.exists():
        click.echo(f"Vault '{vault_name}' does not exist.", err=True)
        raise SystemExit(1)
    vault.load()
    for k, v in sorted(vault.all().items()):
        click.echo(f"{k}={v}")


@cli.command("delete")
@click.argument("vault_name")
@click.argument("key")
@click.password_option(confirmation_prompt=False)
def delete_var(vault_name, key, password):
    """Delete a variable from the vault."""
    vault = Vault(vault_name, password)
    if not vault.exists():
        click.echo(f"Vault '{vault_name}' does not exist.", err=True)
        raise SystemExit(1)
    vault.load()
    if not vault.delete(key):
        click.echo(f"Key '{key}' not found.", err=True)
        raise SystemExit(1)
    vault.save()
    click.echo(f"Deleted {key}.")


cli.add_command(sync)
cli.add_command(audit)
cli.add_command(tag)
cli.add_command(profile)
cli.add_command(history)
cli.add_command(rotate)
cli.add_command(search)


if __name__ == "__main__":
    cli()
