"""Click implementation of commands for the collaborator resource using
Click.

Functions:
    collaborator    # click.group to organize commands under 'collaborator'
    create          # Start the creation of a new collaborator and its
                    # associated user
    read            # Query database and display a table
    update          # Update a specific collaborator
    delete          # Delete a specific collaborator
    assign_role     # Change a specific collaborator role
"""
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


@click.group(help="Commands to manage collaborators.")
def collaborator():
    """Top level command group for collaborators."""
    pass


@click.command(help="Create a new collaborator and its user credentials.")
@click.option("-d", "--data-collaborator",
              type=click.STRING,
              nargs=2,
              multiple=True,
              help="Key-value pairs with collaborator data. "
                   "(ex: --data-collaborator email user@mail.com)")
@click.option("-np", "--no-prompt", is_flag=True, default=False,
              help="Disable interactive prompting for missing fields.")
def create(data_collaborator, no_prompt):
    """Creates a new collaborator and a new user with mandatory username
    and password. Display the new collaborator information when
    transaction is successful.

    Args:
        data_collaborator (iter(tuple[str, str])): the tuples contain
            information about the new collaborator.
        no_prompt (bool): block interactive prompt, false by default.
    """
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


@click.command(help="Read collaborators from the database.")
@click.option("-pk", "-PK",
              type=click.IntRange(min_open=1),
              help="Collaborator's unique id, pk: INT >= 1")
@click.option("-f", "--filter", "filters",
              type=click.STRING,
              nargs=2,
              multiple=True,
              help="Key-value pairs to apply filters. "
                   "(ex: --filter last_name Spring --filter role SUPPORT)")
@click.option("-s", "--sort", "sorts",
              type=click.STRING,
              multiple=True,
              help="Keyword:direction to sort by one or more columns. "
                   "(ex: --sort last_name:asc --sort id:desc)")
@click.option("-rc", "--remove-columns", "--remove-column",
              type=click.STRING,
              multiple=True,
              help="Keyword to hide columns from output. "
                   "(ex: --remove-column role)")
def read(pk, filters, sorts, remove_columns):
    """Queries collaborators and print them in a formatted table.

    Args:
        pk (int): The unique ID of the collaborator.
        filters (iter(tuple[str, str])): The tuples contain key-value
            pairs where the key corresponds to the column name and value
            is the filter to apply to the column.
        sorts (tuple[str]): Ordered keyword to use for sorting.
        remove_columns (tuple[str]): List of columns name to remove from
            the table.
    """
    output = cli_read(pk, filters, sorts, CollaboratorManager, KEYS_MAP)
    remove_col = normalize_remove_columns(remove_columns, KEYS_MAP)
    CollaboratorCrudView().render(output, remove_col=remove_col)


@click.command(help="Update a specific collaborators information.")
@click.option("-pk", "-PK",
              type=click.IntRange(min_open=1),
              help="Collaborator's unique id, pk: INT >= 1")
@click.option("-d", "--data-collaborator",
              type=click.STRING,
              nargs=2,
              multiple=True,
              help="Key-value pairs with collaborator data. "
                   "(ex: --data-collaborator email user@mail.com)")
@click.option("-np", "--no-prompt", is_flag=True, default=False,
              help="Disable interactive prompting for missing fields.")
def update(pk, data_collaborator, no_prompt):
    """Lookup for a specific collaborator and update its information
    with the provided data.

    Args:
        pk (int): The unique ID of the collaborator.
        data_collaborator (iter(tuple[str, str])): the tuples contain
            information about the new collaborator.
        no_prompt (bool): block interactive prompt, false by default.
    """
    cli_update(pk, data_collaborator, no_prompt, CollaboratorManager,
               PROMPT_UPDATE, KEYS_MAP)
    CollaboratorCrudView().success("Collaborator successfully updated")


@click.command(help="Delete a specific collaborator and its associated "
                    "user.")
@click.option("-pk", "-PK",
              type=click.IntRange(min_open=1),
              help="Collaborator's unique id, pk: INT >= 1")
def delete(pk):
    """Delete a specific collaborator from the database. It also deletes
    the associated user from the database.

    Args:
        pk (int): The unique ID of the collaborator.
    """
    cli_delete(pk, CollaboratorManager)
    BaseView.success("Collaborator successfully deleted")


@click.command(help="Assign a new role to a collaborator. The roles must be"
                    "a part of [DEACTIVATED, MANAGEMENT, SALES, SUPPORT]")
@click.option("-pk", "-PK",
              type=click.IntRange(min_open=1),
              help="Collaborator's unique id, pk: INT >= 1")
@click.option("-ro", "--role",
              type=click.Choice(
                  [
                      "1",
                      "DEACTIVATED",
                      "3",
                      "MANAGEMENT",
                      "4",
                      "SALES",
                      "5",
                      "SUPPORT"
                  ]
              ),
              nargs=1,
              help="Role type to assign, one of "
                   "[DEACTIVATED, MANAGEMENT, SALES, SUPPORT]")
def assign_role(pk, role):
    """

    Args:
        pk (int): The unique ID of the collaborator.
        role (str): The new role to assign to the collaborator.
    """
    controller = CollaboratorManager()
    controller.change_collaborator_role(pk, role)
    BaseView.success(
        f"Collaborator successfully assigned to new role : {role}")


# Collaborator resource commands
collaborator.add_command(create)
collaborator.add_command(read)
collaborator.add_command(update)
collaborator.add_command(delete)
collaborator.add_command(assign_role)
