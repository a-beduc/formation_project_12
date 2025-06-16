import click

from ee_crm.domain.model import AuthUserError
from ee_crm.services.auth.authentication import AuthenticationError
from ee_crm.services.auth.jwt_handler import NoToken
from ee_crm.controllers import authentication


@click.command()
def login():
    username = click.prompt('Username')
    plain_password = click.prompt('Password', hide_input=True)
    try:
        authentication.login(username, plain_password)
    except (AuthUserError, AuthenticationError) as e:
        error = click.ClickException(f'{e.args[0]}')
        click.echo(error)
        raise SystemExit(1)

    click.echo(f"Logged in as {username}! Proceed with your requests")


@click.command()
def logout():
    try:
        authentication.logout()
    except NoToken as e:
        error = click.ClickException(f'{e.args[0]}')
        click.echo(error)
        click.echo("Already logged out")
        raise SystemExit(1)

    click.echo(f"Successfully logged out")
