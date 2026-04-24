"""CLI commands for managing vault chains."""
import click
from envault.vault import Vault
from envault.chain import set_chain, remove_chain, get_chain, list_chains, run_chain


@click.group()
def chain():
    """Manage and execute key chains."""


@chain.command("add")
@click.argument("vault_name")
@click.argument("chain_name")
@click.argument("steps", nargs=-1, required=True)
@click.password_option(prompt="Vault password")
def add_cmd(vault_name, chain_name, steps, password):
    """Define a named chain of vault keys."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    try:
        set_chain(v.data, chain_name, list(steps))
    except ValueError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    v.save()
    click.echo(f"Chain '{chain_name}' saved with {len(steps)} step(s).")


@chain.command("remove")
@click.argument("vault_name")
@click.argument("chain_name")
@click.password_option(prompt="Vault password")
def remove_cmd(vault_name, chain_name, password):
    """Remove a named chain."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    removed = remove_chain(v.data, chain_name)
    if removed:
        v.save()
        click.echo(f"Chain '{chain_name}' removed.")
    else:
        click.echo(f"Chain '{chain_name}' not found.", err=True)


@chain.command("list")
@click.argument("vault_name")
@click.password_option(prompt="Vault password")
def list_cmd(vault_name, password):
    """List all defined chains."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    names = list_chains(v.data)
    if not names:
        click.echo("No chains defined.")
    else:
        for name in names:
            steps = get_chain(v.data, name)
            click.echo(f"{name}: {' -> '.join(steps)}")


@chain.command("run")
@click.argument("vault_name")
@click.argument("chain_name")
@click.password_option(prompt="Vault password")
def run_cmd(vault_name, chain_name, password):
    """Run a chain and print resolved values."""
    v = Vault(vault_name, password)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v.load()
    try:
        results = run_chain(v.data, chain_name)
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    steps = get_chain(v.data, chain_name)
    for key, value in zip(steps, results):
        click.echo(f"{key}={value}")
