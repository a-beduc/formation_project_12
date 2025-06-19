from ee_crm.cli_interface.views.view_base_crud import CrudView


class UserCrudView(CrudView):
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
