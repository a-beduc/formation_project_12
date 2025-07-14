import click

from ee_crm.cli_interface.app.cli_func import cli_prompt, cli_read, \
    cli_update, cli_delete
from ee_crm.cli_interface.utils import clean_input_fields, normalize_fields, \
    map_accepted_key, normalize_remove_columns
from ee_crm.cli_interface.views.view_base import BaseView
from ee_crm.cli_interface.views.view_collaborator import CollaboratorCrudView
from ee_crm.controllers.app.collaborator import CollaboratorManager
from ee_crm.controllers.app.user import UserManager

_EXPAND_ACCEPTED_KEYS = {
    "id": {"id"},
    "last_name": {"ln", "last name", "last_name"},
    "first_name": {"fn", "first name", "first_name"},
    "email": {"at", "email", "e_mail"},
    "phone_number": {"ph", "phone number", "phone_number"},
    "role": {"ro", "role"},
    "user_id": {"ui", "uid", "user id", "user_id"}
}
KEYS_MAP = map_accepted_key(_EXPAND_ACCEPTED_KEYS)

PROMPT_CREATE = (
    ("last_name", "string"),
    ("first_name", "string"),
    ("email", "string"),
    ("phone_number", "20 char max"),
    ("role", "DEACTIVATED, MANAGEMENT, SALES, SUPPORT")
)

PROMPT_UPDATE = (
    ("last_name", "string"),
    ("first_name", "string"),
    ("email", "string"),
    ("phone_number", "20 char max")
)


@click.group()
def collaborator():
    pass


@click.command()
@click.option("-d", "--data-collaborator",
              type=click.STRING,
              nargs=2,
              multiple=True,
              help="optional data about collaborator")
@click.option("-np", "--no-prompt", is_flag=True, default=False,
              help="flag to turn off prompting to get additional data")
def create(data_collaborator, no_prompt):
    controller = CollaboratorManager()

    username = click.prompt('create username')
    password = click.prompt('create password (8 char, 1 upper, 1 lower, '
                            '1 number)', hide_input=True)
    password_2 = click.prompt('confirm password', hide_input=True)

    UserManager.verify_plain_password_match(password, password_2)

    cl_data = clean_input_fields(data_collaborator) or {}
    norm_data = normalize_fields(cl_data, KEYS_MAP) or {}
    comp_data = cli_prompt(norm_data, no_prompt, PROMPT_CREATE)

    output = controller.create(username, password, **comp_data)

    viewer = CollaboratorCrudView()
    viewer.success(f"User {username} successfully created")
    viewer.render(output)


@click.command()
@click.option("-pk", "-PK",
              type=click.IntRange(min_open=1),
              help="Collaborator's unique id, pk: INT >= 1")
@click.option("-f", "--filter", "filters",
              type=click.STRING,
              nargs=2,
              multiple=True,
              help="KEY VALUE pair to apply a filter")
@click.option("-s", "--sort", "sorts",
              type=click.STRING,
              multiple=True,
              help="Ordered KEYs to apply a sort to the result of the query "
                   "field:asc, field:desc")
@click.option("-rc", "--remove-columns", "--remove-column",
              type=click.STRING,
              multiple=True,
              help="Columns names to remove from result")
def read(pk, filters, sorts, remove_columns):
    output = cli_read(pk, filters, sorts, CollaboratorManager, KEYS_MAP)
    remove_col = normalize_remove_columns(remove_columns, KEYS_MAP)
    CollaboratorCrudView().render(output, remove_col=remove_col)


@click.command()
@click.option("-pk", "-PK",
              type=click.IntRange(min_open=1),
              help="Collaborator's unique id, pk: INT >= 1")
@click.option("-d", "--data-collaborator",
              type=click.STRING,
              nargs=2,
              multiple=True,
              help="optional data about collaborator")
@click.option("-np", "--no-prompt", is_flag=True, default=False,
              help="flag to turn off prompting to get additional data")
def update(pk, data_collaborator, no_prompt):
    cli_update(pk, data_collaborator, no_prompt, CollaboratorManager,
               PROMPT_UPDATE, KEYS_MAP)
    CollaboratorCrudView().success(f"Collaborator successfully updated")


@click.command()
@click.option("-pk", "-PK",
              type=click.IntRange(min_open=1),
              help="Collaborator's unique id, pk: INT >= 1")
def delete(pk):
    cli_delete(pk, CollaboratorManager)
    BaseView.success(f"Collaborator successfully deleted")


@click.command()
@click.option("-pk", "-PK",
              type=click.IntRange(min_open=1),
              help="Collaborator's unique id, pk: INT >= 1")
@click.option("-ro", "--role",
              type=click.Choice(
                  [
                      1,
                      "DEACTIVATED",
                      3,
                      "MANAGEMENT",
                      4,
                      "SALES",
                      5,
                      "SUPPORT"
                  ]
              ),
              nargs=1,
              help="One of [DEACTIVATED, MANAGEMENT, SALES, SUPPORT]")
def assign_role(pk, role):
    controller = CollaboratorManager()
    controller.change_collaborator_role(pk, role)
    BaseView.success(
        f"Collaborator successfully assigned to new role : {role}")


collaborator.add_command(create)
collaborator.add_command(read)
collaborator.add_command(update)
collaborator.add_command(delete)
collaborator.add_command(assign_role)
