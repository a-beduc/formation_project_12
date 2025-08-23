"""Class that implement the view for the Contract resource.

Class:
    ContractCrudView  # View for the Contract resource.
"""
from ee_crm.cli_interface.views.view_base_crud import CrudView


class ContractCrudView(CrudView):
    """CRUD view for the Contract resource.

    Attributes (class):
        label (str): Used for the title and identification of the table.
        columns (list[str]): Ordered columns name.
        weight_width_allocation (dict) : Mapping between columns name
            and relative allocated width.
        max_width_allocation (dict): Mapping between columns name and
            maximum allocated width.
    """
    label = "Contract"
    columns = ['id', 'total_amount', 'due_amount', 'created_at', 'signed',
               'client_id']
    weight_width_allocation = {
        "id": 5,
        "total_amount": 10,
        "due_amount": 10,
        "created_at": 20,
        "signed": 10,
        "client_id": 5
    }
    max_width_allocation = {
        "id": 6,
        "total_amount": 12,
        "due_amount": 12,
        "created_at": 20,
        "signed": 10,
        "client_id": 6
    }
