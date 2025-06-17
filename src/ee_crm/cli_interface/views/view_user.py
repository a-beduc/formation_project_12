from ee_crm.cli_interface.views.view_base import BaseView


class UserView(BaseView):
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
