"""CLI commands for profile management."""

import click
from envault.vault import Vault
from envault.profiles import (
    save_profile,
    delete_profile,
    get_profile,
    list_profiles,
    apply_profile,
)
from envault.export import to_shell_exports, to_dotenv


@click.group()
def profile():
    """Manage profiles (named sets of variables)."""
    pass


@profile.command("save")
@click.argument("name")
@click.argument("keys", nargs=-1, required=True)
@click.option("--vault", "vault_name", default="default", show_default=True)
@click.password_option(prompt="Vault password")
def save_cmd(name, keys, vault_name, password):
    """Save a named profile with the given variable keys."""
    v = Vault(vault_name, password)
    save_profile(v.data, name, list(keys))
    v.save()
    click.echo(f"Profile '{name}' saved with {len(keys)} key(s).")


@profile.command("delete")
@click.argument("name")
@click.option("--vault", "vault_name", default="default", show_default=True)
@click.password_option(prompt="Vault password")
def delete_cmd(name, vault_name, password):
    """Delete a profile."""
    v = Vault(vault_name, password)
    if delete_profile(v.data, name):
        v.save()
        click.echo(f"Profile '{name}' deleted.")
    else:
        click.echo(f"Profile '{name}' not found.", err=True)


@profile.command("list")
@click.option("--vault", "vault_name", default="default", show_default=True)
@click.password_option(prompt="Vault password")
def list_cmd(vault_name, password):
    """List all profiles."""
    v = Vault(vault_name, password)
    names = list_profiles(v.data)
    if not names:
        click.echo("No profiles defined.")
    for name in names:
        keys = get_profile(v.data, name) or []
        click.echo(f"{name}: {', '.join(keys)}")


@profile.command("apply")
@click.argument("name")
@click.option("--vault", "vault_name", default="default", show_default=True)
@click.option("--format", "fmt", type=click.Choice(["export", "dotenv"]), default="export", show_default=True)
@click.password_option(prompt="Vault password")
def apply_cmd(name, vault_name, fmt, password):
    """Output variables from a profile."""
    v = Vault(vault_name, password)
    vars_ = apply_profile(v.data, name)
    if vars_ is None:
        click.echo(f"Profile '{name}' not found.", err=True)
        return
    if fmt == "dotenv":
        click.echo(to_dotenv(vars_))
    else:
        click.echo(to_shell_exports(vars_))
