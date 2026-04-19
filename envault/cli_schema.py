"""CLI commands for schema validation."""

import click
from envault.vault import Vault
from envault import schema as sch


@click.group()
def schema():
    """Manage variable schema rules."""


@schema.command("set")
@click.argument("vault_name")
@click.argument("key")
@click.option("--type", "type_", required=True, type=click.Choice(["string", "integer", "boolean", "float"]), help="Expected type")
@click.option("--required", is_flag=True, default=False, help="Mark as required")
@click.password_option(prompt="Vault password")
def set_cmd(vault_name, key, type_, required, password):
    """Define a schema rule for KEY."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    sch.define_schema(v.data, key, type_, required)
    v.save()
    click.echo(f"Schema set: {key} -> {type_}" + (" (required)" if required else ""))


@schema.command("remove")
@click.argument("vault_name")
@click.argument("key")
@click.password_option(prompt="Vault password")
def remove_cmd(vault_name, key, password):
    """Remove schema rule for KEY."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    removed = sch.remove_schema(v.data, key)
    if removed:
        v.save()
        click.echo(f"Schema rule for '{key}' removed.")
    else:
        click.echo(f"No schema rule found for '{key}'.")


@schema.command("list")
@click.argument("vault_name")
@click.password_option(prompt="Vault password")
def list_cmd(vault_name, password):
    """List all schema rules."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    rules = sch.list_schema(v.data)
    if not rules:
        click.echo("No schema rules defined.")
    for key, rule in rules.items():
        req = " [required]" if rule.get("required") else ""
        click.echo(f"  {key}: {rule['type']}{req}")


@schema.command("validate")
@click.argument("vault_name")
@click.password_option(prompt="Vault password")
def validate_cmd(vault_name, password):
    """Validate vault vars against schema."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    errors = sch.validate_vault(v.data)
    if not errors:
        click.echo("All variables pass schema validation.")
    else:
        for e in errors:
            click.echo(f"  ERROR: {e}")
        raise SystemExit(1)
