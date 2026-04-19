"""CLI commands for managing key dependencies."""

import click
from envault.vault import Vault
from envault import dependency as dep


@click.group()
def dependency():
    """Manage key dependencies."""
    pass


@dependency.command("add")
@click.argument("vault_name")
@click.argument("key")
@click.argument("depends_on")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def add_cmd(vault_name, key, depends_on, password):
    """Add a dependency: KEY depends on DEPENDS_ON."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    try:
        dep.add_dependency(v.data, key, depends_on)
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    v.save()
    click.echo(f"Added: {key} depends on {depends_on}.")


@dependency.command("remove")
@click.argument("vault_name")
@click.argument("key")
@click.argument("depends_on")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def remove_cmd(vault_name, key, depends_on, password):
    """Remove a dependency between KEY and DEPENDS_ON."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    removed = dep.remove_dependency(v.data, key, depends_on)
    if removed:
        v.save()
        click.echo(f"Removed dependency: {key} -> {depends_on}.")
    else:
        click.echo(f"Dependency not found.", err=True)


@dependency.command("show")
@click.argument("vault_name")
@click.argument("key")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def show_cmd(vault_name, key, password):
    """Show dependencies for KEY."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    deps = dep.get_dependencies(v.data, key)
    dependents = dep.get_dependents(v.data, key)
    click.echo(f"'{key}' depends on: {deps if deps else '(none)'}")
    click.echo(f"Keys depending on '{key}': {dependents if dependents else '(none)'}")


@dependency.command("check")
@click.argument("vault_name")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def check_cmd(vault_name, password):
    """Check for missing dependencies in the vault."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    missing = dep.check_missing_dependencies(v.data)
    if not missing:
        click.echo("All dependencies satisfied.")
    else:
        for key, absent in missing.items():
            click.echo(f"  {key}: missing {absent}")
