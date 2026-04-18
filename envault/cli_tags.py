"""CLI commands for tagging vault variables."""
import click
from envault.vault import Vault
from envault import tags as tag_module


@click.group()
def tag():
    """Manage tags on vault variables."""
    pass


@tag.command("add")
@click.argument("vault_name")
@click.argument("key")
@click.argument("tag")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def add_tag(vault_name, key, tag, password):
    """Add a TAG to KEY in VAULT_NAME."""
    v = Vault(vault_name, password)
    v.load()
    if key not in v.data:
        raise click.ClickException(f"Key '{key}' not found in vault.")
    tag_module.set_tag(v.data, key, tag)
    v.save()
    click.echo(f"Tag '{tag}' added to '{key}'.")


@tag.command("remove")
@click.argument("vault_name")
@click.argument("key")
@click.argument("tag")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def remove_tag(vault_name, key, tag, password):
    """Remove a TAG from KEY in VAULT_NAME."""
    v = Vault(vault_name, password)
    v.load()
    removed = tag_module.remove_tag(v.data, key, tag)
    if not removed:
        raise click.ClickException(f"Tag '{tag}' not found on key '{key}'.")
    v.save()
    click.echo(f"Tag '{tag}' removed from '{key}'.")


@tag.command("list")
@click.argument("vault_name")
@click.argument("tag")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def list_by_tag(vault_name, tag, password):
    """List all keys in VAULT_NAME with the given TAG."""
    v = Vault(vault_name, password)
    v.load()
    keys = tag_module.list_by_tag(v.data, tag)
    if not keys:
        click.echo(f"No keys found with tag '{tag}'.")
    else:
        for key in keys:
            click.echo(key)


@tag.command("all")
@click.argument("vault_name")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def all_tags(vault_name, password):
    """List all unique tags used in VAULT_NAME."""
    v = Vault(vault_name, password)
    v.load()
    t_list = tag_module.all_tags(v.data)
    if not t_list:
        click.echo("No tags defined.")
    else:
        for t in t_list:
            click.echo(t)
