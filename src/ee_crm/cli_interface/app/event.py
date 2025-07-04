import click

from ee_crm.cli_interface.app.cli_func import cli_create, cli_read, \
    cli_update, cli_delete, cli_mine, cli_clean
from ee_crm.cli_interface.utils import map_accepted_key, \
    normalize_remove_columns, clean_input_fields, normalize_fields, clean_sort, \
    normalize_sort
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


@click.command("assign-support")
@click.option("-pk", "-PK",
              type=click.IntRange(min_open=1),
              help="Event's unique id, pk: INT >= 1")
@click.option("-si", "-sui", "-co", "-cui", "--supporter", "--collaborator",
              type=click.IntRange(min_open=1),
              help="Collaborator's unique id, pk: INT >= 1")
@click.option("-ua", "--unassign", is_flag=True, default=False,
              help="flag to remove the support without replacing them.")
def assign_support(event_id, supporter, unassign):
    if unassign is True:
        supporter = None
    controller = EventManager()
    controller.change_support(event_id, supporter, unassign)
    BaseView.success(f"Event ({event_id}) successfully updated")


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
    output = cli_mine(filters, sorts, EventManager, KEYS_MAP)
    remove_col = normalize_remove_columns(remove_columns, KEYS_MAP)
    EventCrudView().render(output, remove_col=remove_col)


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
def unassigned(filters, sorts, remove_columns):
    controller = EventManager()
    norm_filters, norm_sorts = cli_clean(filters, sorts, KEYS_MAP)
    output = controller.unassigned_events(norm_filters, norm_sorts)

    remove_col = normalize_remove_columns(remove_columns, KEYS_MAP)
    EventCrudView().render(output, remove_col=remove_col)


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
    controller = EventManager()
    norm_filters, norm_sorts = cli_clean(filters, sorts, KEYS_MAP)
    output = controller.orphan_events(norm_filters, norm_sorts)

    remove_col = normalize_remove_columns(remove_columns, KEYS_MAP)
    EventCrudView().render(output, remove_col=remove_col)


event.add_command(create)
event.add_command(read)
event.add_command(update)
event.add_command(delete)
event.add_command(assign_support)
event.add_command(show_mine)
event.add_command(unassigned)
event.add_command(orphan)
