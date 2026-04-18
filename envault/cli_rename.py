"""CLI commands for rename and alias operations."""

import click
from envault.vault import Vault
from envault.rename import rename_key, set_alias, remove_alias, list_aliases, resolve_alias


@click.group()
def rename():
    """Rename keys and manage aliases."""
    pass


@rename.command("key")
@click.argument("vault_name")
@click.argument("old_key")
@click.argument("new_key")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite new_key if it exists.")
def rename_key_cmd(vault_name, old_key, new_key, password, overwrite):
    """Rename OLD_KEY to NEW_KEY in VAULT_NAME."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    try:
        rename_key(v.data, old_key, new_key, overwrite=overwrite)
    except (KeyError, ValueError) as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    v.save()
    click.echo(f"Renamed '{old_key}' -> '{new_key}'.")


@rename.command("alias")
@click.argument("vault_name")
@click.argument("key")
@click.argument("alias")
@click.option("--password", prompt=True, hide_input=True)
def alias_cmd(vault_name, key, alias, password):
    """Create an ALIAS pointing to KEY in VAULT_NAME."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    try:
        set_alias(v.data, key, alias)
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    v.save()
    click.echo(f"Alias '{alias}' -> '{key}' created.")


@rename.command("unalias")
@click.argument("vault_name")
@click.argument("alias")
@click.option("--password", prompt=True, hide_input=True)
def unalias_cmd(vault_name, alias, password):
    """Remove ALIAS from VAULT_NAME."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    removed = remove_alias(v.data, alias)
    if not removed:
        click.echo(f"Alias '{alias}' not found.", err=True)
        raise SystemExit(1)
    v.save()
    click.echo(f"Alias '{alias}' removed.")


@rename.command("aliases")
@click.argument("vault_name")
@click.option("--password", prompt=True, hide_input=True)
def list_aliases_cmd(vault_name, password):
    """List all aliases in VAULT_NAME."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    aliases = list_aliases(v.data)
    if not aliases:
        click.echo("No aliases defined.")
    else:
        for alias, key in aliases.items():
            click.echo(f"{alias} -> {key}")
