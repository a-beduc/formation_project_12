import click

from ee_crm.cli_interface.app.cli_func import cli_create, cli_read, \
    cli_update, cli_delete
from ee_crm.cli_interface.utils import map_accepted_key, \
    normalize_remove_columns
from ee_crm.cli_interface.views.view_base import BaseView
from ee_crm.cli_interface.views.view_event import EventCrudView
from ee_crm.controllers.app.event import EventManager


_EXPAND_ACCEPTED_KEYS = {
    "id": {"id"},
    "title": {"ti", "title"},
    "start_time": {"st", "start time", "start_time"},
    "end_time": {"et", "end time", "end_time"},
    "location": {"lo", "location"},
    "attendee": {"at", "attendee"},
    "notes": {"no", "notes"},
    "supporter_id": {"su", "si", "supporter", "supporter id", "supporter_id",
                     "support_id", "support id"},
    "contract_id": {"co", "ci", "contract", "contract id", "contract_id"}
}
KEYS_MAP = map_accepted_key(_EXPAND_ACCEPTED_KEYS)

PROMPT_CREATE = (
    ("title", "string"),
    ("start_time", "string; format : 'YYYY-MM-DD HH:mm:ss'"),
    ("end_time", "string; format : 'YYYY-MM-DD HH:mm:ss'"),
    ("location", "string"),
    ("attendee", "integer"),
    ("notes", "string"),
    ("contract_id", "integer")
)

PROMPT_UPDATE = (
    ("title", "string"),
    ("start_time", "string; format : 'YYYY-MM-DD HH:mm:ss'"),
    ("end_time", "string; format : 'YYYY-MM-DD HH:mm:ss'"),
    ("location", "string"),
    ("attendee", "integer"),
    ("notes", "string")
)


@click.group()
def event():
    pass


@click.command()
@click.option('-d', "--data-event",
              type=click.STRING,
              nargs=2,
              multiple=True,
              help="optional data about event")
@click.option("-np", "--no-prompt", is_flag=True, default=False,
              help="flag to turn off prompting to get additional data")
def create(data_event, no_prompt):
    output = cli_create(data_event, no_prompt, EventManager,
                        PROMPT_CREATE, KEYS_MAP)
    viewer = EventCrudView()
    viewer.success("Event successfully created")
    viewer.render(output)


@click.command()
@click.option("-pk", "-PK",
              type=click.IntRange(min_open=1),
              help="Event's unique id, pk: INT >= 1")
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
    output = cli_read(pk, filters, sorts, EventManager, KEYS_MAP)
    remove_col = normalize_remove_columns(remove_columns, KEYS_MAP)
    EventCrudView().render(output, remove_col=remove_col)


@click.command()
@click.option("-pk", "-PK",
              type=click.IntRange(min_open=1),
              help="Event's unique id, pk: INT >= 1")
@click.option("-d", "--data-event",
              type=click.STRING,
              nargs=2,
              multiple=True,
              help="optional data about collaborator")
@click.option("-np", "--no-prompt", is_flag=True, default=False,
              help="flag to turn off prompting to get additional data")
def update(pk, data_event, no_prompt):
    cli_update(pk, data_event, no_prompt, EventManager,
               PROMPT_UPDATE, KEYS_MAP)
    BaseView.success(f"Event successfully updated")


@click.command()
@click.option("-pk", "-PK",
              type=click.IntRange(min_open=1),
              help="Event's unique id, pk: INT >= 1")
def delete(pk):
    cli_delete(pk, EventManager)
    BaseView.success(f"Event successfully deleted")


event.add_command(create)
event.add_command(read)
event.add_command(update)
event.add_command(delete)
