import click

from ee_crm.cli_interface.views.view_base import BaseView
from ee_crm.controllers.auth import authentication


@click.command()
def login():
    username = click.prompt('Username')
    plain_password = click.prompt('Password', hide_input=True)
    authentication.login(username, plain_password)
    BaseView().success(f"Logged in as {username}! Proceed with your requests")


@click.command()
def logout():
    authentication.logout()
    BaseView().success("Successfully logged out")
