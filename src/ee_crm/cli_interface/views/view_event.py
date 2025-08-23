"""Class that implement the view for the Event resource.

Class:
    EventCrudView  # View for the Event resource.
"""
from ee_crm.cli_interface.views.view_base_crud import CrudView


class EventCrudView(CrudView):
    """CRUD view for the Event resource.

    Attributes (class):
        label (str): Used for the title and identification of the table.
        columns (list[str]): Ordered columns name.
        weight_width_allocation (dict) : Mapping between columns name
            and relative allocated width.
        max_width_allocation (dict): Mapping between columns name and
            maximum allocated width.
    """
    label = "Event"
    columns = ['id', 'title', 'start_time', 'end_time', 'location',
               'attendee', 'notes', 'supporter_id', 'contract_id']
    weight_width_allocation = {
        "id": 5,
        "title": 15,
        "start_time": 15,
        "end_time": 15,
        "location": 10,
        "attendee": 5,
        "notes": 30,
        "supporter_id": 5,
        "contract_id": 5
    }
    max_width_allocation = {
        "id": 6,
        "title": 20,
        "start_time": 20,
        "end_time": 20,
        "location": 30,
        "attendee": 6,
        "notes": 100,
        "supporter_id": 6,
        "contract_id": 6
    }
