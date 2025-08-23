"""Class that implement the view for the User resource.

Class:
    UserCrudView  # View for the User resource.
"""
from ee_crm.cli_interface.views.view_base_crud import CrudView


class UserCrudView(CrudView):
    """CRUD view for the User resource.

    Attributes (class):
        label (str): Used for the title and identification of the table.
        columns (list[str]): Ordered columns name.
        weight_width_allocation (dict) : Mapping between columns name
            and relative allocated width.
        max_width_allocation (dict): Mapping between columns name and
            maximum allocated width.
    """
    label = "User"
    columns = ['id', 'username']
    weight_width_allocation = {
        "id": 5,
        "username": 15,
    }
    max_width_allocation = {
        "id": 6,
        "username": 20
    }
