"""CLI commands for conditional variables."""

import click
from envault.vault import Vault
from envault.condvar import set_condvar, remove_condvar, get_condvar, list_condvars, apply_condvars


@click.group()
def condvar():
    """Manage conditional variable rules."""


@condvar.command("add")
@click.argument("key")
@click.argument("source")
@click.option("--when", "conditions", multiple=True, metavar="VALUE:RESULT",
              required=True, help="Condition in VALUE:RESULT format")
@click.option("--default", default=None, help="Default value when no condition matches")
@click.option("--vault", "vault_name", required=True)
@click.option("--password", prompt=True, hide_input=True)
def add_cmd(key, source, conditions, default, vault_name, password):
    """Add a conditional variable rule."""
    from envault.storage import vault_exists
    if not vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v = Vault(vault_name, password)
    v.load()
    parsed = {}
    for cond in conditions:
        if ":" not in cond:
            click.echo(f"Invalid condition format '{cond}'. Use VALUE:RESULT.", err=True)
            raise SystemExit(1)
        val, result = cond.split(":", 1)
        parsed[val] = result
    try:
        set_condvar(v.data, key, source, parsed, default)
    except (KeyError, ValueError) as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    v.save()
    click.echo(f"Condvar rule added: {key} depends on {source}.")


@condvar.command("remove")
@click.argument("key")
@click.option("--vault", "vault_name", required=True)
@click.option("--password", prompt=True, hide_input=True)
def remove_cmd(key, vault_name, password):
    """Remove a conditional variable rule."""
    from envault.storage import vault_exists
    if not vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v = Vault(vault_name, password)
    v.load()
    if remove_condvar(v.data, key):
        v.save()
        click.echo(f"Condvar rule for '{key}' removed.")
    else:
        click.echo(f"No condvar rule found for '{key}'.")


@condvar.command("list")
@click.option("--vault", "vault_name", required=True)
@click.option("--password", prompt=True, hide_input=True)
def list_cmd(vault_name, password):
    """List all conditional variable rules."""
    from envault.storage import vault_exists
    if not vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v = Vault(vault_name, password)
    v.load()
    rules = list_condvars(v.data)
    if not rules:
        click.echo("No condvar rules defined.")
        return
    for key, rule in rules.items():
        conds = ", ".join(f"{k}->{val}" for k, val in rule["conditions"].items())
        default_str = f" (default: {rule['default']})" if rule.get("default") else ""
        click.echo(f"  {key} <- {rule['source']}: {conds}{default_str}")


@condvar.command("apply")
@click.option("--vault", "vault_name", required=True)
@click.option("--password", prompt=True, hide_input=True)
def apply_cmd(vault_name, password):
    """Evaluate and apply all condvar rules to current vars."""
    from envault.storage import vault_exists
    if not vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v = Vault(vault_name, password)
    v.load()
    apply_condvars(v.data)
    v.save()
    click.echo("Condvar rules applied.")
