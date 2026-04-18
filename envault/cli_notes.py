"""CLI commands for managing per-key notes."""

import click
from envault.vault import Vault
from envault import notes as notes_mod


@click.group()
def note():
    """Manage notes attached to vault keys."""
    pass


@note.command("set")
@click.argument("vault_name")
@click.argument("key")
@click.argument("note")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def set_note(vault_name, key, note, password):
    """Attach a note to KEY in VAULT_NAME."""
    v = Vault(vault_name, password)
    if not v.load():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    if key not in v.data.get("vars", {}):
        click.echo(f"Key '{key}' does not exist in vault.", err=True)
        raise SystemExit(1)
    notes_mod.set_note(v.data, key, note)
    v.save()
    click.echo(f"Note set for '{key}'.")


@note.command("get")
@click.argument("vault_name")
@click.argument("key")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def get_note(vault_name, key, password):
    """Show the note attached to KEY."""
    v = Vault(vault_name, password)
    if not v.load():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    n = notes_mod.get_note(v.data, key)
    if n is None:
        click.echo(f"No note for '{key}'.")
    else:
        click.echo(n)


@note.command("remove")
@click.argument("vault_name")
@click.argument("key")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def remove_note(vault_name, key, password):
    """Remove the note attached to KEY."""
    v = Vault(vault_name, password)
    if not v.load():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    removed = notes_mod.remove_note(v.data, key)
    if removed:
        v.save()
        click.echo(f"Note removed for '{key}'.")
    else:
        click.echo(f"No note found for '{key}'.")


@note.command("list")
@click.argument("vault_name")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def list_notes(vault_name, password):
    """List all notes in VAULT_NAME."""
    v = Vault(vault_name, password)
    if not v.load():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    all_notes = notes_mod.list_notes(v.data)
    if not all_notes:
        click.echo("No notes found.")
    else:
        for k, n in all_notes.items():
            click.echo(f"{k}: {n}")
