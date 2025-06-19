import click

from ee_crm.cli_interface.app.cli_func import cli_read
from ee_crm.cli_interface.utils import normalize_remove_columns, \
    map_accepted_key
from ee_crm.cli_interface.views.view_base import BaseView
from ee_crm.cli_interface.views.view_user import UserCrudView
from ee_crm.controllers.app.user import UserManager


_EXPAND_ACCEPTED_KEYS = {
    "id": {"id"},
    "username": {"us", "un", "user name", "username"}
}
KEYS_MAP = map_accepted_key(_EXPAND_ACCEPTED_KEYS)


@click.group()
def user():
    pass


@click.command()
@click.option("-pk", "-PK",
              type=click.IntRange(min_open=1),
              help="Contract's unique id, pk: INT >= 1")
@click.option("-f", "--filters", "--filter",
              type=click.STRING,
              nargs=2,
              multiple=True,
              help="KEY VALUE pair to apply a filter")
@click.option("-s", "--sorts", "--sort",
              type=click.STRING,
              multiple=True,
              help="Ordered KEYs to apply a sort to the result of the query "
                   "field:asc, field:desc")
@click.option("-rc", "--remove-columns", "--remove-column",
              type=click.STRING,
              multiple=True,
              help="Columns names to remove from result")
def read(pk, filters, sorts, remove_columns):
    output = cli_read(pk, filters, sorts, UserManager, KEYS_MAP)
    remove_col = normalize_remove_columns(remove_columns, KEYS_MAP)
    UserCrudView().render(output, remove_col=remove_col)


@click.command("whoami")
def who_am_i():
    controller = UserManager()
    user_dto, coll_dto = controller.who_am_i()
    BaseView.success(f'Logged in as ({user_dto.id}) {user_dto.username} !')
    BaseView.success(f'Welcome {coll_dto.first_name} {coll_dto.last_name}, '
                     f'your role is {coll_dto.role}')


@click.command("change_username")
def change_username():
    controller = UserManager()
    old_username = click.prompt("Current username")
    plain_password = click.prompt('Password', hide_input=True)
    new_username = click.prompt("New username")

    if not click.confirm(f'Confirm changing username from {old_username} '
                         f'to {new_username} ?'):
        raise controller.error_cls('Aborted')

    controller.update_username(old_username, plain_password, new_username)
    BaseView.success(f'Username successfully updated : {new_username}')


@click.command("change_password")
def change_password():
    controller = UserManager()
    username = click.prompt("Username")
    old_plain_password = click.prompt('Old password', hide_input=True)
    new_plain_password = click.prompt('New password', hide_input=True)
    confirm_new_plain_password = click.prompt('Confirm new password',
                                              hide_input=True)

    UserManager.verify_plain_password_match(old_plain_password,
                                            new_plain_password)

    if not click.confirm(f'Confirm changing your password ?'):
        raise controller.error_cls('Aborted')

    controller.update_username(username, old_plain_password, new_plain_password)
    BaseView.success("Password successfully updated")


user.add_command(read)
user.add_command(change_username)
user.add_command(change_password)
