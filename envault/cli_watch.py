"""CLI commands for watching a vault for changes."""
import click
from envault.storage import vault_exists
from envault.watch import watch_vault


@click.group()
def watch():
    """Watch a vault for changes."""
    pass


@watch.command("start")
@click.argument("vault_name")
@click.option("--interval", default=1.0, show_default=True, help="Polling interval in seconds.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password (for display only).")
def start_cmd(vault_name: str, interval: float, password: str) -> None:
    """Watch VAULT_NAME and print a message whenever it changes."""
    if not vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' does not exist.", err=True)
        raise SystemExit(1)

    click.echo(f"Watching vault '{vault_name}' every {interval}s. Press Ctrl+C to stop.")

    def on_change(name: str) -> None:
        click.echo(f"[changed] Vault '{name}' was updated.")

    try:
        watch_vault(vault_name, on_change, interval=interval)
    except KeyboardInterrupt:
        click.echo("\nStopped watching.")
