"""CLI commands for managing value transform pipelines."""

import click
from envault.vault import Vault
from envault import transform as tf


@click.group()
def transform():
    """Manage value transform pipelines."""


@transform.command("set")
@click.argument("vault_name")
@click.argument("key")
@click.argument("steps", nargs=-1, required=True)
@click.option("--password", prompt=True, hide_input=True)
def set_cmd(vault_name, key, steps, password):
    """Attach a transform pipeline (ordered STEPS) to KEY."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    try:
        tf.set_pipeline(v.data, key, list(steps))
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    v.save()
    click.echo(f"Pipeline set for '{key}': {' | '.join(steps)}")


@transform.command("remove")
@click.argument("vault_name")
@click.argument("key")
@click.option("--password", prompt=True, hide_input=True)
def remove_cmd(vault_name, key, password):
    """Remove the transform pipeline from KEY."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    removed = tf.remove_pipeline(v.data, key)
    if removed:
        v.save()
        click.echo(f"Pipeline removed from '{key}'.")
    else:
        click.echo(f"No pipeline found for '{key}'.")


@transform.command("show")
@click.argument("vault_name")
@click.argument("key")
@click.option("--password", prompt=True, hide_input=True)
def show_cmd(vault_name, key, password):
    """Show the transform pipeline and resolved value for KEY."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    pipeline = tf.get_pipeline(v.data, key)
    resolved = tf.resolve_value(v.data, key)
    if resolved is None:
        click.echo(f"Key '{key}' not found.", err=True)
        raise SystemExit(1)
    if pipeline:
        click.echo(f"Pipeline : {' | '.join(pipeline)}")
    else:
        click.echo("Pipeline : (none)")
    click.echo(f"Resolved : {resolved}")


@transform.command("list")
def list_cmd():
    """List all available built-in transforms."""
    for name in tf.list_transforms():
        click.echo(f"  {name}")


def register(cli):
    cli.add_command(transform)
