"""Service to extract specific information needed by the access control
layer. If the target entity is missing or the attribute is broken, the
service returns 'None' instead of raising an error.

Classes
    PermissionService   # collection of methods to extract specific info
"""


class PermissionService:
    """Utility collection of helpers used by the access control layer.

    Args
        uow (AbstractUnitOfWork): Unit of work exposing 'clients',
            'contracts' and 'events' repositories.
    """
    def __init__(self, uow):
        self.uow = uow

    def get_client_associated_salesman(self, client_id):
        """Return the ID of the salesman responsible for the given
        client.

        Args
            client_id (int): Primary key of the client.

        Return
            int | None: ID of the salesman responsible for the given
                client or 'None' if not found.
        """
        with self.uow:
            try:
                return self.uow.clients.get(client_id).salesman_id
            except AttributeError:
                return None

    def get_contract_associated_salesman(self, contract_id):
        """Return the ID of the salesman linked to the contract's
        client.

        Args
            contract_id (int): Primary key of the contract.

        Return
            int | None: ID of the salesman responsible for the given
                client or 'None' if not found.
        """
        with self.uow:
            try:
                return self.uow.contracts.get(contract_id).client.salesman_id
            except AttributeError:
                return None

    def get_contract_signed(self, contract_id):
        """Return the state of the contract as a boolean. True if
        signed, False otherwise.

        Args
            contract_id (int): Primary key of the contract.

        Return
            bool | None: True if the contract is signed, False
                otherwise and None if not found.
        """
        with self.uow:
            try:
                return self.uow.contracts.get(contract_id).signed
            except AttributeError:
                return None

    def get_event_support(self, event_id):
        """Return the collaborator assigned to support the event.

        Args
            event_id (int): Primary key of the event.

        Return
            int | None: ID of the collaborator assigned to the event or
                None if not found.
        """
        with self.uow:
            try:
                return self.uow.events.get(event_id).supporter_id
            except AttributeError:
                return None

    def get_event_associated_salesman(self, event_id):
        """Return the ID of the salesman linked to the contract for the
        given event.

        Args
            event_id (int): Primary key of the event.

        Return
            int | None: ID of the salesman responsible for the given
                event or 'None' if not found.
        """
        with self.uow:
            try:
                return self.uow.events.get(
                    event_id).contract.client.salesman_id
            except AttributeError:
                return None
