"""Implementation of Click command for the authentication processes.

Functions
    login
    logout
"""
import click

from ee_crm.cli_interface.views.view_base import BaseView
from ee_crm.controllers.auth import authentication


@click.command(help="Login with your username and password.")
def login():
    """Login command.

    Prompts for username and password, then authenticates the user.
    """
    username = click.prompt('Username')
    plain_password = click.prompt('Password', hide_input=True)
    authentication.login(username, plain_password)
    BaseView().success(f"Logged in as {username}! Proceed with your requests")


@click.command(help="Logout the current user.")
def logout():
    """Logout command.

    Remove the locally stored token used for authentication.
    """
    authentication.logout()
    BaseView().success("Successfully logged out")
