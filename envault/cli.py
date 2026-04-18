import sys
import click
from envault.vault import Vault


@click.group()
def cli():
    """envault — manage and sync environment variables using encrypted local storage."""
    pass


@cli.command()
@click.argument("vault_name")
@click.password_option(prompt="Master password", confirmation_prompt=True)
def init(vault_name, password):
    """Initialize a new vault."""
    from envault.storage import vault_exists
    if vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' already exists.", err=True)
        sys.exit(1)
    vault = Vault(vault_name, password)
    vault.save()
    click.echo(f"Vault '{vault_name}' created successfully.")


@cli.command(name="set")
@click.argument("vault_name")
@click.argument("key")
@click.argument("value")
@click.password_option(prompt="Master password", confirmation_prompt=False)
def set_var(vault_name, key, value, password):
    """Set an environment variable in the vault."""
    try:
        vault = Vault.load(vault_name, password)
        vault.set(key, value)
        vault.save()
        click.echo(f"Set '{key}' in vault '{vault_name}'.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command(name="get")
@click.argument("vault_name")
@click.argument("key")
@click.password_option(prompt="Master password", confirmation_prompt=False)
def get_var(vault_name, key, password):
    """Get an environment variable from the vault."""
    try:
        vault = Vault.load(vault_name, password)
        value = vault.get(key)
        if value is None:
            click.echo(f"Key '{key}' not found.", err=True)
            sys.exit(1)
        click.echo(value)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command(name="list")
@click.argument("vault_name")
@click.password_option(prompt="Master password", confirmation_prompt=False)
def list_vars(vault_name, password):
    """List all keys in the vault."""
    try:
        vault = Vault.load(vault_name, password)
        keys = vault.list_keys()
        if not keys:
            click.echo("No variables stored.")
        for key in keys:
            click.echo(key)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("vault_name")
@click.password_option(prompt="Master password", confirmation_prompt=False)
def export(vault_name, password):
    """Export vault variables as shell export statements."""
    try:
        vault = Vault.load(vault_name, password)
        for key, value in vault.all().items():
            click.echo(f"export {key}={value!r}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command(name="vaults")
def list_vaults_cmd():
    """List all available vaults."""
    from envault.storage import list_vaults
    vaults = list_vaults()
    if not vaults:
        click.echo("No vaults found.")
    for name in vaults:
        click.echo(name)


if __name__ == "__main__":
    cli()
