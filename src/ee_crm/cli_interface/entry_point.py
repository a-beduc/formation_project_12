import click

from ee_crm.cli_interface.authentication import login, logout
from ee_crm.cli_interface.collaborator import collaborator


@click.group
def cli():
    pass


cli.add_command(login)
cli.add_command(logout)
cli.add_command(collaborator)
