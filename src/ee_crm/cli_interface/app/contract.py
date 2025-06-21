import click

from ee_crm.cli_interface.app.cli_func import cli_create, cli_read, cli_delete
from ee_crm.cli_interface.utils import map_accepted_key, \
    normalize_remove_columns
from ee_crm.cli_interface.views.view_base import BaseView
from ee_crm.cli_interface.views.view_contract import ContractCrudView
from ee_crm.controllers.app.contract import ContractManager


_EXPAND_ACCEPTED_KEYS = {
        "id": {"id"},
        "total_amount": {"ta", "total amount", "total_amount"},
        "paid_amount": {"pa", "first name", "paid_amount"},
        "signed": {"si", "signed"},
        "client_id": {"cl", "ci", "client id", "client_id"},
        "created_at": {"ca", "created at", "created_at"}
    }
KEYS_MAP = map_accepted_key(_EXPAND_ACCEPTED_KEYS)

PROMPT_FIELDS = (
    ("total_amount", "price"),
    ("client_id", "integer")
)


@click.group()
def contract():
    pass


@click.command()
@click.option('-d', "--data-contract",
              type=click.STRING,
              nargs=2,
              multiple=True,
              help="optional data about contract")
@click.option("-np", "--no-prompt", is_flag=True, default=False,
              help="flag to turn off prompting to get additional data")
def create(data_contract, no_prompt):
    output = cli_create(data_contract, no_prompt, ContractManager,
                        PROMPT_FIELDS, KEYS_MAP)
    viewer = ContractCrudView()
    viewer.success("Contract successfully created")
    viewer.render(output)


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
    output = cli_read(pk, filters, sorts, ContractManager, KEYS_MAP)
    remove_col = normalize_remove_columns(remove_columns, KEYS_MAP)
    ContractCrudView().render(output, remove_col=remove_col)


@click.command()
@click.option("-pk", "-PK",
              type=click.IntRange(min_open=1),
              help="Contract's unique id, pk: INT >= 1")
def delete(pk):
    cli_delete(pk, ContractManager)
    BaseView.success(f"Contract successfully deleted")


contract.add_command(create)
contract.add_command(read)
contract.add_command(delete)
