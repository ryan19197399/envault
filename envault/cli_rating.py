"""CLI commands for vault key quality ratings."""

from __future__ import annotations

import click

from envault.storage import vault_exists, load_vault
from envault.rating import rate_key, rate_all, rating_summary


@click.group()
def rating() -> None:
    """Key quality rating commands."""


@rating.command("show")
@click.argument("vault_name")
@click.argument("key")
def show_cmd(vault_name: str, key: str) -> None:
    """Show quality rating for a single KEY."""
    if not vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' does not exist.", err=True)
        raise SystemExit(1)
    vault_data = load_vault(vault_name)
    try:
        result = rate_key(vault_data, key)
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)

    click.echo(f"Key   : {result['key']}")
    click.echo(f"Score : {result['score']}/{result['max']}")
    click.echo(f"Locked: {'yes' if result['immutable'] else 'no'}")
    click.echo("Breakdown:")
    for criterion, info in result["breakdown"].items():
        status = "✓" if info["passed"] else "✗"
        click.echo(f"  {status} {criterion:<15} ({info['weight']} pts)")


@rating.command("all")
@click.argument("vault_name")
@click.option("--min-score", default=0, show_default=True, help="Only show keys at or above this score.")
def all_cmd(vault_name: str, min_score: int) -> None:
    """Show ratings for all keys in VAULT_NAME."""
    if not vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' does not exist.", err=True)
        raise SystemExit(1)
    vault_data = load_vault(vault_name)
    results = [r for r in rate_all(vault_data) if r["score"] >= min_score]
    if not results:
        click.echo("No keys match the criteria.")
        return
    for r in results:
        click.echo(f"{r['score']:>3}/100  {r['key']}")


@rating.command("summary")
@click.argument("vault_name")
def summary_cmd(vault_name: str) -> None:
    """Print aggregate rating statistics for VAULT_NAME."""
    if not vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' does not exist.", err=True)
        raise SystemExit(1)
    vault_data = load_vault(vault_name)
    stats = rating_summary(vault_data)
    click.echo(f"Keys   : {stats['count']}")
    click.echo(f"Average: {stats['average']}")
    click.echo(f"Min    : {stats['min']}")
    click.echo(f"Max    : {stats['max']}")


def register(parent: click.Group) -> None:
    parent.add_command(rating)
