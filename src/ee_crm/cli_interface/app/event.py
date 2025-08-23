"""Click implementation of commands for the event resource using Click.

Functions:
    event           # click.group to organize commands under 'event'
    create          # Start the creation of a new event
    read            # Query database and display a table
    update          # Update a specific event
    delete          # Delete a specific event
    assign_support  # Assign or remove a support from an event
    show_mine       # Show events linked to the logged user
    unassigned      # Show events without attributed support
    orphan          # Show events without a salesman
"""
import click

from ee_crm.cli_interface.app.cli_func import cli_create, cli_read, \
    cli_update, cli_delete, cli_mine, cli_clean
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


@click.group(help="Commands to manage events.")
def event():
    """Top level command group for event."""
    pass


@click.command(help="Create a new event.")
@click.option('-d', "--data-event",
              type=click.STRING,
              nargs=2,
              multiple=True,
              help="optional data about event. "
                   "(ex: --data-event notes text)")
@click.option("-np", "--no-prompt", is_flag=True, default=False,
              help="Disable interactive prompting for missing fields.")
def create(data_event, no_prompt):
    """Create a new event. Display the new event information when
    transaction is successful.

    Args:
        data_event (iter(tuple[str, str])): the tuples contain
            information about the new event.
        no_prompt (bool): block interactive prompt, false by default.
    """
    output = cli_create(data_event, no_prompt, EventManager,
                        PROMPT_CREATE, KEYS_MAP)
    viewer = EventCrudView()
    viewer.success("Event successfully created")
    viewer.render(output)


@click.command(help="Read events from the database.")
@click.option("-pk", "-PK",
              type=click.IntRange(min_open=1),
              help="Event's unique id, pk: INT >= 1")
@click.option("-f", "--filters", "--filter",
              type=click.STRING,
              nargs=2,
              multiple=True,
              help="Key-value pairs to apply filters. "
                   "(ex: --filter title party)")
@click.option("-s", "--sorts", "--sort",
              type=click.STRING,
              multiple=True,
              help="Ordered KEYs to apply a sort to the result of the query "
                   "(ex: field:asc, field:desc)")
@click.option("-rc", "--remove-columns", "--remove-column",
              type=click.STRING,
              multiple=True,
              help="Keyword to hide columns from output. "
                   "(ex: --remove-column title)")
def read(pk, filters, sorts, remove_columns):
    """Queries events and print them in a formatted table.

    Args:
        pk (int): The unique ID of the event.
        filters (iter(tuple[str, str])): The tuples contain key-value
            pairs where the key corresponds to the column name and value
            is the filter to apply to the column.
        sorts (tuple[str]): Ordered keyword to use for sorting.
        remove_columns (tuple[str]): List of columns name to remove from
            the table.
    """
    output = cli_read(pk, filters, sorts, EventManager, KEYS_MAP)
    remove_col = normalize_remove_columns(remove_columns, KEYS_MAP)
    EventCrudView().render(output, remove_col=remove_col)


@click.command(help="Update a specific event information in the database.")
@click.option("-pk", "-PK",
              type=click.IntRange(min_open=1),
              help="Event's unique id, pk: INT >= 1")
@click.option("-d", "--data-event",
              type=click.STRING,
              nargs=2,
              multiple=True,
              help="optional data about event. "
                   "(ex: --data-event notes text)")
@click.option("-np", "--no-prompt", is_flag=True, default=False,
              help="Disable interactive prompting for missing fields.")
def update(pk, data_event, no_prompt):
    """Lookup for a specific events and update its information with the
    provided data.

    Args:
        pk (int): The unique ID of the event.
        data_event (iter(tuple[str, str])): the tuples contain
            information about the new event.
        no_prompt (bool): block interactive prompt, false by default.
    """
    cli_update(pk, data_event, no_prompt, EventManager,
               PROMPT_UPDATE, KEYS_MAP)
    BaseView.success("Event successfully updated")


@click.command(help="Delete a specific event.")
@click.option("-pk", "-PK",
              type=click.IntRange(min_open=1),
              help="Event's unique id, pk: INT >= 1")
def delete(pk):
    """Delete a specific event from the database.

    Args:
        pk (int): The unique ID of the event.
    """
    cli_delete(pk, EventManager)
    BaseView.success("Event successfully deleted")


@click.command("assign-support",
               help="Assign a new support for the event, can unassign.")
@click.option("-pk", "-PK",
              type=click.IntRange(min_open=1),
              help="Event's unique id, pk: INT >= 1")
@click.option("-si", "-sui", "-co", "-cui", "--supporter", "--collaborator",
              type=click.IntRange(min_open=1),
              help="Collaborator's unique id, pk: INT >= 1")
@click.option("-ua", "--unassign", is_flag=True, default=False,
              help="flag to remove the support without replacing them.")
def assign_support(event_id, supporter, unassign):
    """Assign a support for the event, can also remove support from an
     event without assigning a new one.

    Args:
        event_id (int): The unique ID (or PK) of the event.
        supporter (int): The unique ID (or PK) of the collaborator.
        unassign (bool): flag to unassign the support.
    """
    if unassign:
        supporter = None
    controller = EventManager()
    controller.change_support(event_id, supporter, unassign)
    BaseView.success(f"Event ({event_id}) successfully updated")


@click.command(help="Display the information of event linked to the user.")
@click.option("-f", "--filters", "--filter",
              type=click.STRING,
              nargs=2,
              multiple=True,
              help="Key-value pairs to apply filters. "
                   "(ex: --filter title party)")
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
    """Display the information of events linked to the user.

    Args:
        filters (iter(tuple[str, str])): The tuples contain key-value
            pairs where the key corresponds to the column name and value
            is the filter to apply to the column.
        sorts (tuple[str]): Ordered keyword to use for sorting.
        remove_columns (tuple[str]): List of columns name to remove from
            the table.
    """
    output = cli_mine(filters, sorts, EventManager, KEYS_MAP)
    remove_col = normalize_remove_columns(remove_columns, KEYS_MAP)
    EventCrudView().render(output, remove_col=remove_col)


@click.command(help="Display events without support.")
@click.option("-f", "--filters", "--filter",
              type=click.STRING,
              nargs=2,
              multiple=True,
              help="Key-value pairs to apply filters. "
                   "(ex: --filter title party)")
@click.option("-s", "--sorts", "--sort",
              type=click.STRING,
              multiple=True,
              help="Ordered KEYs to apply a sort to the result of the query "
                   "(ex: field:asc, field:desc)")
@click.option("-rc", "--remove-columns", "--remove-column",
              type=click.STRING,
              multiple=True,
              help="Disable interactive prompting for missing fields.")
def unassigned(filters, sorts, remove_columns):
    """Display the information of events without support.

    Args:
        filters (iter(tuple[str, str])): The tuples contain key-value
            pairs where the key corresponds to the column name and value
            is the filter to apply to the column.
        sorts (tuple[str]): Ordered keyword to use for sorting.
        remove_columns (tuple[str]): List of columns name to remove from
            the table.
    """
    controller = EventManager()
    norm_filters, norm_sorts = cli_clean(filters, sorts, KEYS_MAP)
    output = controller.unassigned_events(norm_filters, norm_sorts)

    remove_col = normalize_remove_columns(remove_columns, KEYS_MAP)
    EventCrudView().render(output, remove_col=remove_col)


@click.command(help="Display events without linked contract.")
@click.option("-f", "--filters", "--filter",
              type=click.STRING,
              nargs=2,
              multiple=True,
              help="Key-value pairs to apply filters. "
                   "(ex: --filter title party)")
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
    """Display the information of events without linked contract.

    Args:
        filters (iter(tuple[str, str])): The tuples contain key-value
            pairs where the key corresponds to the column name and value
            is the filter to apply to the column.
        sorts (tuple[str]): Ordered keyword to use for sorting.
        remove_columns (tuple[str]): List of columns name to remove from
            the table.
    """
    controller = EventManager()
    norm_filters, norm_sorts = cli_clean(filters, sorts, KEYS_MAP)
    output = controller.orphan_events(norm_filters, norm_sorts)

    remove_col = normalize_remove_columns(remove_columns, KEYS_MAP)
    EventCrudView().render(output, remove_col=remove_col)


# Event resource commands
event.add_command(create)
event.add_command(read)
event.add_command(update)
event.add_command(delete)
event.add_command(assign_support)
event.add_command(show_mine)
event.add_command(unassigned)
event.add_command(orphan)
