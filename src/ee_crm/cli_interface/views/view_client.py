from ee_crm.cli_interface.views.view_base import BaseView


class ClientView(BaseView):
    label = "Client"
    columns = ['id', 'last_name', 'first_name', 'email', 'phone_number',
               'company', 'created_at', 'updated_at', 'salesman_id']
    weight_width_allocation = {
        "id": 5,
        "last_name": 15,
        "first_name": 15,
        "email": 20,
        "phone_number": 10,
        "company": 15,
        "created_at": 15,
        "updated_at": 15,
        "salesman_id": 5,
    }
    max_width_allocation = {
        "id": 6,
        "last_name": 20,
        "first_name": 20,
        "email": 30,
        "phone_number": 20,
        "company": 25,
        "created_at": 20,
        "updated_at": 20,
        "salesman_id": 6,
    }
