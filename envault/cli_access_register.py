"""Register access commands into the main CLI."""

from envault.cli_access import access


def register(cli):
    """Attach the access command group to the root CLI."""
    cli.add_command(access)
