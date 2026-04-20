"""CLI commands for cascade rules."""
import click
from envault.vault import Vault
from envault.cascade import set_cascade, remove_cascade, list_cascades, apply_cascades


@click.group()
def cascade():
    """Manage cascade propagation rules between keys."""
    pass


@cascade.command("add")
@click.argument("vault_name")
@click.argument("source_key")
@click.argument("target_key")
@click.option("--transform", default=None, help="Transform to apply: upper, lower, strip.")
@click.password_option("--password", prompt="Vault password")
def add_cmd(vault_name, source_key, target_key, transform, password):
    """Add a cascade rule from SOURCE_KEY to TARGET_KEY."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    try:
        set_cascade(v.data, source_key, target_key, transform)
    except (KeyError, ValueError) as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    v.save()
    msg = f"Cascade: {source_key} -> {target_key}"
    if transform:
        msg += f" (transform: {transform})"
    click.echo(msg)


@cascade.command("remove")
@click.argument("vault_name")
@click.argument("source_key")
@click.password_option("--password", prompt="Vault password")
def remove_cmd(vault_name, source_key, password):
    """Remove the cascade rule for SOURCE_KEY."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    removed = remove_cascade(v.data, source_key)
    if removed:
        v.save()
        click.echo(f"Cascade rule for '{source_key}' removed.")
    else:
        click.echo(f"No cascade rule found for '{source_key}'.")


@cascade.command("list")
@click.argument("vault_name")
@click.password_option("--password", prompt="Vault password")
def list_cmd(vault_name, password):
    """List all cascade rules in a vault."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    rules = list_cascades(v.data)
    if not rules:
        click.echo("No cascade rules defined.")
        return
    for r in rules:
        t = f" [{r['transform']}]" if r["transform"] else ""
        click.echo(f"  {r['source']} -> {r['target']}{t}")


@cascade.command("apply")
@click.argument("vault_name")
@click.argument("source_key")
@click.password_option("--password", prompt="Vault password")
def apply_cmd(vault_name, source_key, password):
    """Manually trigger cascade propagation for SOURCE_KEY."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    updated = apply_cascades(v.data, source_key)
    if updated:
        v.save()
        click.echo(f"Updated keys: {', '.join(updated)}")
    else:
        click.echo(f"No cascade rule found for '{source_key}'.")
