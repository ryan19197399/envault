"""CLI commands for managing webhooks."""
import click
from envault.vault import Vault
from envault.webhook import set_webhook, remove_webhook, list_webhooks, fire_webhook


@click.group()
def webhook():
    """Manage webhook notifications."""


@webhook.command("add")
@click.argument("vault_name")
@click.argument("url")
@click.option("--events", default=None, help="Comma-separated event names, or * for all.")
@click.password_option(prompt="Vault password")
def add_cmd(vault_name, url, events, password):
    """Register a webhook URL for a vault."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    event_list = [e.strip() for e in events.split(",")] if events else None
    set_webhook(v.data, url, event_list)
    v.save()
    click.echo(f"Webhook registered: {url}")


@webhook.command("remove")
@click.argument("vault_name")
@click.argument("url")
@click.password_option(prompt="Vault password")
def remove_cmd(vault_name, url, password):
    """Remove a registered webhook."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    if remove_webhook(v.data, url):
        v.save()
        click.echo(f"Webhook removed: {url}")
    else:
        click.echo(f"Webhook not found: {url}", err=True)
        raise SystemExit(1)


@webhook.command("list")
@click.argument("vault_name")
@click.password_option(prompt="Vault password")
def list_cmd(vault_name, password):
    """List all registered webhooks."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    hooks = list_webhooks(v.data)
    if not hooks:
        click.echo("No webhooks registered.")
        return
    for h in hooks:
        events = ", ".join(h["events"])
        click.echo(f"{h['url']}  events=[{events}]  added={h['created_at']}")


@webhook.command("fire")
@click.argument("vault_name")
@click.argument("event")
@click.password_option(prompt="Vault password")
def fire_cmd(vault_name, event, password):
    """Manually fire a test event to all matching webhooks."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    results = fire_webhook(v.data, event, {"manual": True})
    for url, ok in results:
        status = "OK" if ok else "FAILED"
        click.echo(f"  {status}  {url}")
    if not results:
        click.echo("No webhooks matched.")
