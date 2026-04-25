"""CLI commands for linting vault contents."""

import click
from envault.vault import Vault
from envault.lint import run_lint


@click.group()
def lint():
    """Lint vault variables for common issues."""
    pass


@lint.command("check")
@click.argument("vault_name")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--strict", is_flag=True, default=False, help="Exit with non-zero code if issues found.")
@click.option("--only", multiple=True,
              type=click.Choice(["naming", "empty", "duplicates", "ttl"], case_sensitive=False),
              help="Run only specific lint checks.")
def check_cmd(vault_name, password, strict, only):
    """Run lint checks against a vault."""
    try:
        v = Vault.load(vault_name, password)
    except FileNotFoundError:
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error loading vault: {e}", err=True)
        raise SystemExit(1)

    results = run_lint(v.data, checks=list(only) if only else None)

    if not results:
        click.echo(click.style("✔ No issues found.", fg="green"))
        return

    total = sum(len(issues) for issues in results.values())
    click.echo(click.style(f"Found {total} issue(s):\n", fg="yellow"))

    for check_name, issues in results.items():
        if not issues:
            continue
        click.echo(click.style(f"  [{check_name}]", fg="cyan", bold=True))
        for issue in issues:
            key = issue.get("key", "<vault>")
            message = issue.get("message", "")
            click.echo(f"    • {key}: {message}")
        click.echo()

    if strict and total > 0:
        raise SystemExit(1)
