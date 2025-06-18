import click

from ee_crm.cli_interface.authentication import login, logout
from ee_crm.cli_interface.app.client import client
from ee_crm.cli_interface.app.collaborator import collaborator
from ee_crm.cli_interface.app.contract import contract
from ee_crm.cli_interface.app.event import event
from ee_crm.cli_interface.app.user import user, who_am_i


@click.group
def cli():
    pass


cli.add_command(login)
cli.add_command(logout)
cli.add_command(who_am_i)

cli.add_command(user)
cli.add_command(collaborator)
cli.add_command(client)
cli.add_command(contract)
cli.add_command(event)
