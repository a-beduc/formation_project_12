from ee_crm.cli_interface.views.view_base import BaseView


class ContractView(BaseView):
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
