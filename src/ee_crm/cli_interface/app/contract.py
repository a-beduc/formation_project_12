"""Click implementation of commands for the contract resource using
Click.

Once created, contract can only be updated through specific methods to
ensure consistency and minimize errors.

Functions:
    contract    # click.group to organize commands under 'contract'
    create      # Start the creation of a new contract
    read        # Query database and display a table
    delete      # Delete a specific contract
    sign        # Sign a contract, cannot be undone
    new_total   # Change total, only when contract is unsigned
    pay         # Begin contract payment, only when contract is signed
    show_mine   # Show contracts linked to the logged user
    orphan      # Show contracts without a client
"""
from math import trunc

import click

from ee_crm.cli_interface.app.cli_func import cli_clean, cli_create, \
    cli_delete, cli_read
from ee_crm.cli_interface.utils import normalize_remove_columns, \
    map_accepted_key
from ee_crm.cli_interface.views.view_base import BaseView
from ee_crm.cli_interface.views.view_contract import ContractCrudView
from ee_crm.controllers.app.contract import ContractManager
from ee_crm.exceptions import ContractServiceError

_EXPAND_ACCEPTED_KEYS = {
    "id": {"id"},
    "total_amount": {"ta", "total amount", "total_amount"},
    "due_amount": {"da", "due amount", "due_amount"},
    "signed": {"si", "signed"},
    "client_id": {"cl", "ci", "client id", "client_id"},
    "created_at": {"ca", "created at", "created_at"}
}
KEYS_MAP = map_accepted_key(_EXPAND_ACCEPTED_KEYS)

PROMPT_FIELDS = (
    ("total_amount", "price"),
    ("client_id", "integer")
)


@click.group(help="Commands to manage contracts.")
def contract():
    """Top level command group for contract."""
    pass


@click.command(help="Create a new contract.")
@click.option('-d', "--data-contract",
              type=click.STRING,
              nargs=2,
              multiple=True,
              help="optional data about contract. "
                   "(ex: --data-contract total_amount 100)")
@click.option("-np", "--no-prompt", is_flag=True, default=False,
              help="Disable interactive prompting for missing fields.")
def create(data_contract, no_prompt):
    """Create a new contract. Display the new contract information when
    transaction is successful.

    Args:
        data_contract (iter(tuple[str, str])): the tuples contain
            information about the new contract.
        no_prompt (bool): block interactive prompt, false by default.
    """
    output = cli_create(data_contract, no_prompt, ContractManager,
                        PROMPT_FIELDS, KEYS_MAP)
    viewer = ContractCrudView()
    viewer.success("Contract successfully created.")
    viewer.render(output)


@click.command(help="Read contracts from the database.")
@click.option("-pk", "-PK",
              type=click.IntRange(min_open=1),
              help="Contract's unique id, pk: INT >= 1")
@click.option("-f", "--filters", "--filter",
              type=click.STRING,
              nargs=2,
              multiple=True,
              help="Key-value pairs to apply filters. "
                   "(ex: --filter total_amount 100)")
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
    """Queries for contracts and print them in a formatted table.

    Args:
        pk (int): The unique ID of the contract.
        filters (iter(tuple[str, str])): The tuples contain key-value
            pairs where the key corresponds to the column name and value
            is the filter to apply to the column.
        sorts (tuple[str]): Ordered keyword to use for sorting.
        remove_columns (tuple[str]): List of columns name to remove from
            the table.
    """
    output = cli_read(pk, filters, sorts, ContractManager, KEYS_MAP)
    remove_col = normalize_remove_columns(remove_columns, KEYS_MAP)
    ContractCrudView().render(output, remove_col=remove_col)


@click.command(help="Delete a specific contract.")
@click.option("-pk", "-PK",
              type=click.IntRange(min_open=1),
              help="Contract's unique id, pk: INT >= 1")
def delete(pk):
    """Delete a specific contract from the database.

    Args:
        pk (int): The unique ID of the contract.
    """
    cli_delete(pk, ContractManager)
    BaseView.success(f"Contract successfully deleted.")


@click.command(help="Sign an unsigned contract.")
@click.option("-pk", "-PK",
              type=click.IntRange(min_open=1),
              help="Contract's unique id, pk: INT >= 1")
def sign(pk):
    """Sign an unsigned contract.
    If the contract is already signed, display a warning message.

    Args:
        pk (int): The unique ID of the contract.

    Raises:
        ContractServiceError: When a contract is already signed, display
            a warning message.
    """
    controller = ContractManager()
    try:
        controller.sign(pk)
        BaseView.success("Contract successfully signed.")
    except ContractServiceError as e:
        BaseView.warning(e.tips)


@click.command(help="Change the total of an unsigned contract.")
@click.option("-pk", "-PK",
              type=click.IntRange(min_open=1),
              help="Contract's unique id, pk: INT >= 1")
@click.option("-a", "-ta", "--amount", "--total-amount",
              type=click.FloatRange(min_open=0),
              help="Contract's total price, amount: PRICE >= 0")
def new_total(pk, amount):
    """Change the total of an unsigned contract.

    Args:
        pk (int): The unique ID of the contract.
        amount (float): The total amount of an unsigned contract.
    """
    controller = ContractManager()
    controller.change_total(pk, amount)
    new_amount = trunc(amount * 100) / 100
    BaseView.success(f"Contract successfully updated, new total amount : "
                     f"{new_amount}.")


@click.command(help="Add a client's payment to a signed contract.")
@click.option("-pk", "-PK",
              type=click.IntRange(min_open=1),
              help="Contract's unique id, pk: INT >= 1")
@click.option("-a", "-ta", "--amount", "--total-amount",
              type=click.FloatRange(min_open=0),
              help="Contract payment, amount: PRICE >= 0")
def pay(pk, amount):
    """Add a client's payment to a signed contract.

    Args:
        pk (int): The unique ID of the contract.
        amount (float): The total amount of an unsigned contract.
    """
    controller = ContractManager()
    controller.pay(pk, amount)
    new_amount = trunc(amount * 100) / 100
    BaseView.success(f"Contract successfully updated, due amount reduced by "
                     f"{new_amount}.")


@click.command(help="Display contract linked to the logged user.")
@click.option("-nop", "--unpaid",
              is_flag=True, default=False,
              help="Filter out fully paid contracts")
@click.option("-nos", "--unsigned",
              is_flag=True, default=False,
              help="Filter out fully signed contracts")
@click.option("-noe", "--no-event",
              is_flag=True, default=False,
              help="Filter out contracts linked to an event")
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
def show_mine(unpaid, unsigned, no_event, filters, sorts, remove_columns):
    """Display contract linked to the logged user.

    Args:
        unpaid (bool): Filter out fully paid contracts
        unsigned (bool): Filter out fully signed contracts
        no_event (bool): Filter out contracts already linked to an event
        filters (iter(tuple[str, str])): The tuples contain key-value
            pairs where the key corresponds to the column name and value
            is the filter to apply to the column.
        sorts (tuple[str]): Ordered keyword to use for sorting.
        remove_columns (tuple[str]): List of columns name to remove from
            the table.
    """
    controller = ContractManager()
    norm_filters, norm_sorts = cli_clean(filters, sorts, KEYS_MAP)
    output = controller.user_associated_contracts(unpaid, unsigned, no_event,
                                                  norm_filters, norm_sorts)

    remove_col = normalize_remove_columns(remove_columns, KEYS_MAP)

    ContractCrudView().render(output, remove_col=remove_col)


@click.command(help="Display contract not linked to a client.")
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
def orphan(filters, sorts, remove_columns):
    """Display contract not linked to a client.

    Args:
        filters (iter(tuple[str, str])): The tuples contain key-value
            pairs where the key corresponds to the column name and value
            is the filter to apply to the column.
        sorts (tuple[str]): Ordered keyword to use for sorting.
        remove_columns (tuple[str]): List of columns name to remove from
            the table.
    """
    controller = ContractManager()
    norm_filters, norm_sorts = cli_clean(filters, sorts, KEYS_MAP)
    output = controller.orphan_contracts(norm_filters, norm_sorts)

    remove_col = normalize_remove_columns(remove_columns, KEYS_MAP)
    ContractCrudView().render(output, remove_col=remove_col)


# Contract resource commands
contract.add_command(create)
contract.add_command(read)
contract.add_command(delete)
contract.add_command(sign)
contract.add_command(new_total)
contract.add_command(pay)
contract.add_command(show_mine)
contract.add_command(orphan)
