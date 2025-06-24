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


@click.group()
def client():
    pass


@click.command()
@click.option('-d', "--data-client",
              type=click.STRING,
              nargs=2,
              multiple=True,
              help="optional data about client")
@click.option("-np", "--no-prompt", is_flag=True, default=False,
              help="flag to turn off prompting to get additional data")
def create(data_client, no_prompt):
    output = cli_create(data_client, no_prompt, ClientManager,
                        PROMPT_FIELDS, KEYS_MAP)
    viewer = ClientCrudView()
    viewer.success("Client successfully created")
    viewer.render(output)


@click.command()
@click.option("-pk", "-PK",
              type=click.IntRange(min_open=1),
              help="Client's unique id, pk: INT >= 1")
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
    output = cli_read(pk, filters, sorts, ClientManager,
                      KEYS_MAP)
    remove_col = normalize_remove_columns(remove_columns, KEYS_MAP)
    ClientCrudView().render(output, remove_col=remove_col)


@click.command()
@click.option("-pk", "-PK",
              type=click.IntRange(min_open=1),
              help="Client's unique id, pk: INT >= 1")
@click.option("-d", "--data-client",
              type=click.STRING,
              nargs=2,
              multiple=True,
              help="optional data about client")
@click.option("-np", "--no-prompt", is_flag=True, default=False,
              help="flag to turn off prompting to get additional data")
def update(pk, data_client, no_prompt):
    cli_update(pk, data_client, no_prompt, ClientManager,
               PROMPT_FIELDS, KEYS_MAP)
    BaseView.success(f"Client successfully updated")


@click.command()
@click.option("-pk", "-PK",
              type=click.IntRange(min_open=1),
              help="Client's unique id, pk: INT >= 1")
def delete(pk):
    cli_delete(pk, ClientManager)
    BaseView.success(f"Client successfully deleted")


@click.command()
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
def show_mine(filters, sorts, remove_columns):
    controller = ClientManager()
    norm_filters, norm_sorts = cli_clean(filters, sorts, KEYS_MAP)
    output = controller.user_associated_resource(norm_filters, norm_sorts)
    remove_col = normalize_remove_columns(remove_columns, KEYS_MAP)
    ClientCrudView().render(output, remove_col=remove_col)


@click.command()
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
    controller = ClientManager()
    norm_filters, norm_sorts = cli_clean(filters, sorts, KEYS_MAP)
    output = controller.orphan_clients(norm_filters, norm_sorts)
    remove_col = normalize_remove_columns(remove_columns, KEYS_MAP)
    ClientCrudView().render(output, remove_col=remove_col)


client.add_command(create)
client.add_command(read)
client.add_command(update)
client.add_command(delete)
client.add_command(show_mine)
client.add_command(orphan)
