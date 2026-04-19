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
@click.password_option("--password", "-p", prompt=True, confirmation_prompt=False,
                       help="Vault password.")
@click.option("--strict", is_flag=True, default=False,
              help="Exit with non-zero status if any issues found.")
@click.option("--only", multiple=True,
              type=click.Choice(["naming", "empty", "duplicates", "ttl"], case_sensitive=False),
              help="Run only specific lint checks.")
def check_cmd(vault_name, password, strict, only):
    """Run lint checks on a vault and report issues."""
    try:
        vault = Vault.load(vault_name, password)
    except FileNotFoundError:
        click.echo(f"Vault '{vault_name}' does not exist.", err=True)
        raise SystemExit(1)
    except Exception:
        click.echo("Failed to load vault. Wrong password?", err=True)
        raise SystemExit(1)

    results = run_lint(vault.data)

    # Filter by requested checks
    filter_map = {
        "naming": "naming",
        "empty": "empty",
        "duplicates": "duplicates",
        "ttl": "ttl",
    }
    if only:
        selected = {filter_map[o.lower()] for o in only}
        results = {k: v for k, v in results.items() if k in selected}

    total = 0
    for check, issues in results.items():
        if issues:
            click.echo(f"\n[{check.upper()}]")
            for issue in issues:
                click.echo(f"  • {issue}")
            total += len(issues)

    if total == 0:
        click.echo("✓ No issues found.")
    else:
        click.echo(f"\n{total} issue(s) found.")
        if strict:
            raise SystemExit(1)
