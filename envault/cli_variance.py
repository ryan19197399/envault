"""CLI commands for variance tracking."""

import click

from envault.storage import load_vault, save_vault, vault_exists
from envault.variance import (
    check_variance,
    get_baseline,
    remove_baseline,
    set_baseline,
    variance_report,
)


@click.group()
def variance():
    """Track value drift against recorded baselines."""


@variance.command("set")
@click.argument("vault_name")
@click.argument("key")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--value", default=None, help="Explicit baseline value (defaults to current).")
def set_cmd(vault_name, key, password, value):
    """Record the current (or given) value as the baseline for KEY."""
    if not vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    data = load_vault(vault_name, password)
    try:
        baseline = set_baseline(data, key, value)
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    save_vault(vault_name, password, data)
    click.echo(f"Baseline set for '{key}': {baseline}")


@variance.command("remove")
@click.argument("vault_name")
@click.argument("key")
@click.option("--password", prompt=True, hide_input=True)
def remove_cmd(vault_name, key, password):
    """Remove the baseline for KEY."""
    if not vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    data = load_vault(vault_name, password)
    removed = remove_baseline(data, key)
    if not removed:
        click.echo(f"No baseline found for '{key}'.")
        return
    save_vault(vault_name, password, data)
    click.echo(f"Baseline removed for '{key}'.")


@variance.command("check")
@click.argument("vault_name")
@click.argument("key")
@click.option("--password", prompt=True, hide_input=True)
def check_cmd(vault_name, key, password):
    """Check whether KEY has drifted from its baseline."""
    if not vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    data = load_vault(vault_name, password)
    try:
        result = check_variance(data, key)
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    if result["baseline"] is None:
        click.echo(f"No baseline set for '{key}'.")
        return
    status = "DRIFTED" if result["drifted"] else "OK"
    click.echo(f"{key}: [{status}]  baseline={result['baseline']!r}  current={result['current']!r}")


@variance.command("report")
@click.argument("vault_name")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--drifted-only", is_flag=True, help="Only show drifted keys.")
def report_cmd(vault_name, password, drifted_only):
    """Show variance report for all baselined keys."""
    if not vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    data = load_vault(vault_name, password)
    report = variance_report(data)
    if drifted_only:
        report = [r for r in report if r["drifted"]]
    if not report:
        click.echo("No variance data to display.")
        return
    for r in report:
        status = "DRIFTED" if r["drifted"] else "OK"
        click.echo(f"{r['key']}: [{status}]  baseline={r['baseline']!r}  current={r['current']!r}")


def register(parent):
    parent.add_command(variance)
