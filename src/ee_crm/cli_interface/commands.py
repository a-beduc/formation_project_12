"""Contains the list of commands added to the terminal
interface using Click, represented by the click group 'cli'.

Functions:
    cli # click.group to organize commands under the entrypoint "eecrm"

Commands (eecrm <keyword>):
    login
    logout
    whoami

    user
    collaborator
    client
    contract
    event
"""
import click

from ee_crm.cli_interface.app.client import client
from ee_crm.cli_interface.app.collaborator import collaborator
from ee_crm.cli_interface.app.contract import contract
from ee_crm.cli_interface.app.event import event
from ee_crm.cli_interface.app.user import user, who_am_i
from ee_crm.cli_interface.authentication import login, logout


@click.group(help="EECRM CLI interface")
def cli():
    """Click group to organize commands under the entrypoint "eecrm"."""
    pass


# Authentication commands
cli.add_command(login)
cli.add_command(logout)
cli.add_command(who_am_i)

# Resources commands
cli.add_command(user)
cli.add_command(collaborator)
cli.add_command(client)
cli.add_command(contract)
cli.add_command(event)
