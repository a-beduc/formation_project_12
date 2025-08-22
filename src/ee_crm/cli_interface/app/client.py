"""Click implementation of commands for the client resource using Click.

Functions:
    client      # click.group to organize commands under 'client'
    create      # Start the creation of a new client
    read        # Query database and display a table
    update      # Update a specific client
    delete      # Delete a specific client
    show_mine   # Show clients linked to the logged user
    orphan      # Show clients without a salesman
"""
import click

from ee_crm.cli_interface.app.cli_func import cli_create, cli_read, \
    cli_update, cli_delete, cli_clean
from ee_crm.cli_interface.utils import map_accepted_key, \
    normalize_remove_columns
from ee_crm.cli_interface.views.view_base import BaseView
from ee_crm.cli_interface.views.view_client import ClientCrudView
from ee_crm.controllers.app.client import ClientManager

_EXPAND_ACCEPTED_KEYS = {
    "id": {"id"},
    "last_name": {"ln", "last name", "last_name"},
    "first_name": {"fn", "first name", "first_name"},
    "email": {"at", "email", "e_mail"},
    "phone_number": {"ph", "phone number", "phone_number"},
    "company": {"co", "company"},
    "created_at": {"ca", "created at", "created_at"},
    "updated_at": {"ua", "updated at", "updated_at"},
    "salesman_id": {"sa", "si", "salesman id", "salesman",
                    "salesman_id"}
}
KEYS_MAP = map_accepted_key(_EXPAND_ACCEPTED_KEYS)

PROMPT_FIELDS = (
    ("last_name", "string"),
    ("first_name", "string"),
    ("email", "string"),
    ("phone_number", "20 char max"),
    ("company", "string")
)


@click.group(help="Commands to manage clients.")
def client():
    """Top level command group for client."""
    pass


@click.command(help="Create a new client.")
@click.option('-d', "--data-client",
              type=click.STRING,
              nargs=2,
              multiple=True,
              help="optional data about client. "
                   "(ex: --data-client email user@mail.com)")
@click.option("-np", "--no-prompt", is_flag=True, default=False,
              help="Disable interactive prompting for missing fields.")
def create(data_client, no_prompt):
    """Create a new client. Display the new client information when
    transaction is successful.

    Args:
        data_client (iter(tuple[str, str])): the tuples contain
            information about the new client.
        no_prompt (bool): block interactive prompt, false by default.
    """
    output = cli_create(data_client, no_prompt, ClientManager,
                        PROMPT_FIELDS, KEYS_MAP)
    viewer = ClientCrudView()
    viewer.success("Client successfully created")
    viewer.render(output)


@click.command(help="Read clients from the database.")
@click.option("-pk", "-PK",
              type=click.IntRange(min_open=1),
              help="Client's unique id, pk: INT >= 1")
@click.option("-f", "--filters", "--filter",
              type=click.STRING,
              nargs=2,
              multiple=True,
              help="Key-value pairs to apply filters. "
                   "(ex: --filter last_name Spring)")
@click.option("-s", "--sorts", "--sort",
              type=click.STRING,
              multiple=True,
              help="Ordered KEYs to apply a sort to the result of the query "
                   "(ex: field:asc, field:desc)")
@click.option("-rc", "--remove-columns", "--remove-column",
              type=click.STRING,
              multiple=True,
              help="Keyword to hide columns from output. "
                   "(ex: --remove-column email)")
def read(pk, filters, sorts, remove_columns):
    """Queries clients and print them in a formatted table.

    Args:
        pk (int): The unique ID of the client.
        filters (iter(tuple[str, str])): The tuples contain key-value
            pairs where the key corresponds to the column name and value
            is the filter to apply to the column.
        sorts (tuple[str]): Ordered keyword to use for sorting.
        remove_columns (tuple[str]): List of columns name to remove from
            the table.
    """
    output = cli_read(pk, filters, sorts, ClientManager,
                      KEYS_MAP)
    remove_col = normalize_remove_columns(remove_columns, KEYS_MAP)
    ClientCrudView().render(output, remove_col=remove_col)


@click.command(help="Update a specific client information in the "
                    "database.")
@click.option("-pk", "-PK",
              type=click.IntRange(min_open=1),
              help="Client's unique id, pk: INT >= 1")
@click.option("-d", "--data-client",
              type=click.STRING,
              nargs=2,
              multiple=True,
              help="Key-value pairs with client data. "
                   "(ex: --data-client email user@mail.com)")
@click.option("-np", "--no-prompt", is_flag=True, default=False,
              help="Disable interactive prompting for missing fields.")
def update(pk, data_client, no_prompt):
    """Lookup for a specific clients and update its information with the
    provided data.

    Args:
        pk (int): The unique ID of the client.
        data_client (iter(tuple[str, str])): the tuples contain
            information about the new client.
        no_prompt (bool): block interactive prompt, false by default.
    """
    cli_update(pk, data_client, no_prompt, ClientManager,
               PROMPT_FIELDS, KEYS_MAP)
    BaseView.success(f"Client successfully updated")


@click.command(help="Delete a specific client.")
@click.option("-pk", "-PK",
              type=click.IntRange(min_open=1),
              help="Client's unique id, pk: INT >= 1")
def delete(pk):
    """Delete a specific client from the database.

    Args:
        pk (int): The unique ID of the client.
    """
    cli_delete(pk, ClientManager)
    BaseView.success(f"Client successfully deleted")


@click.command(help="Display the information of clients linked to the user.")
@click.option("-f", "--filters", "--filter",
              type=click.STRING,
              nargs=2,
              multiple=True,
              help="Key-value pairs to apply filters. "
                   "(ex: --filter last_name Spring)")
@click.option("-s", "--sorts", "--sort",
              type=click.STRING,
              multiple=True,
              help="Ordered KEYs to apply a sort to the result of the query "
                   "(ex: field:asc, field:desc)")
@click.option("-rc", "--remove-columns", "--remove-column",
              type=click.STRING,
              multiple=True,
              help="Disable interactive prompting for missing fields.")
def show_mine(filters, sorts, remove_columns):
    """Display the information of clients linked to the user.

    Args:
        filters (iter(tuple[str, str])): The tuples contain key-value
            pairs where the key corresponds to the column name and value
            is the filter to apply to the column.
        sorts (tuple[str]): Ordered keyword to use for sorting.
        remove_columns (tuple[str]): List of columns name to remove from
            the table.
    """
    controller = ClientManager()
    norm_filters, norm_sorts = cli_clean(filters, sorts, KEYS_MAP)
    output = controller.user_associated_resource(norm_filters, norm_sorts)
    remove_col = normalize_remove_columns(remove_columns, KEYS_MAP)
    ClientCrudView().render(output, remove_col=remove_col)


@click.command(help="Display clients without linked users.")
@click.option("-f", "--filters", "--filter",
              type=click.STRING,
              nargs=2,
              multiple=True,
              help="Key-value pairs to apply filters. "
                   "(ex: --filter last_name Spring)")
@click.option("-s", "--sorts", "--sort",
              type=click.STRING,
              multiple=True,
              help="Ordered KEYs to apply a sort to the result of the query "
                   "(ex: field:asc, field:desc)")
@click.option("-rc", "--remove-columns", "--remove-column",
              type=click.STRING,
              multiple=True,
              help="Disable interactive prompting for missing fields.")
def orphan(filters, sorts, remove_columns):
    """Display orphan clients without linked users to the database.

    Args:
        filters (iter(tuple[str, str])): The tuples contain key-value
            pairs where the key corresponds to the column name and value
            is the filter to apply to the column.
        sorts (tuple[str]): Ordered keyword to use for sorting.
        remove_columns (tuple[str]): List of columns name to remove from
            the table.
    """
    controller = ClientManager()
    norm_filters, norm_sorts = cli_clean(filters, sorts, KEYS_MAP)
    output = controller.orphan_clients(norm_filters, norm_sorts)
    remove_col = normalize_remove_columns(remove_columns, KEYS_MAP)
    ClientCrudView().render(output, remove_col=remove_col)


# Client resource commands
client.add_command(create)
client.add_command(read)
client.add_command(update)
client.add_command(delete)
client.add_command(show_mine)
client.add_command(orphan)
