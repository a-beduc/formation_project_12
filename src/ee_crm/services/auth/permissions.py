class PermissionService:
    def __init__(self, uow):
        self.uow = uow

    def get_client_associated_salesman(self, client_id):
        with self.uow:
            try:
                return self.uow.clients.get(client_id).salesman_id
            except AttributeError:
                return None

    def get_contract_associated_salesman(self, contract_id):
        with self.uow:
            try:
                return self.uow.contracts.get(contract_id).client.salesman_id
            except AttributeError:
                return None

    def get_contract_signed(self, contract_id):
        with self.uow:
            try:
                return self.uow.contracts.get(contract_id).signed
            except AttributeError:
                return None

    def get_event_support(self, event_id):
        with self.uow:
            try:
                return self.uow.events.get(event_id).supporter_id
            except AttributeError:
                return None

    def get_event_associated_salesman(self, event_id):
        with self.uow:
            try:
                return self.uow.events.get(
                    event_id).contract.client.salesman_id
            except AttributeError:
                return None
