from ee_crm.cli_interface.views.view_base_crud import CrudView


class CollaboratorCrudView(CrudView):
    label = "Collaborator"
    columns = ['id', 'last_name', 'first_name', 'email', 'phone_number',
               'role', 'user_id']
    weight_width_allocation = {
        "id": 5,
        "last_name": 15,
        "first_name": 15,
        "email": 20,
        "phone_number": 10,
        "role": 10,
        "user_id": 5
    }
    max_width_allocation = {
        "id": 6,
        "last_name": 20,
        "first_name": 20,
        "email": 30,
        "phone_number": 20,
        "role": 12,
        "user_id": 6
    }
