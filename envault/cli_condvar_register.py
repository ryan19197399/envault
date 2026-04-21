"""Register condvar commands with the main CLI."""

from envault.cli_condvar import condvar


def register(cli):
    """Attach the condvar command group to the root CLI."""
    cli.add_command(condvar)
