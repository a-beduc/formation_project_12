"""Service layer responsible for Client domain entities.

Classes
    ClientService   # Business operations for clients.
"""
from ee_crm.domain.model import Client
from ee_crm.exceptions import ClientServiceError
from ee_crm.services.app.base import BaseService
from ee_crm.services.dto import ClientDTO


class ClientService(BaseService):
    """Manage clients and enforce business invariants.

    Attributes
        uow (AbstractUnitOfWork): Unit of work exposing repositories.
    """
    def __init__(self, uow):
        super().__init__(
            uow,
            Client,
            ClientDTO,
            ClientServiceError,
            "clients"
        )

    def create(self, salesman_id=None, **kwargs):
        """Create a new client and link it to a salesman.

        Args
            salesman_id (int): Salesman ID.
            **kwargs (Any): Additional keyword arguments for the Client
                builder.

        Returns
            tuple[ClientDTO]: A single element tuple containing the
                DTO of the new Client entity.

        Raises
            ClientServiceError: If the linked collaborator is not a
                salesman
        """
        with self.uow:
            if self.uow.collaborators.get(salesman_id).role.name != "SALES":
                err = self.error_cls("Only sales people can create clients")
                err.tips = ("The collaborator linked to the client must be a "
                            "salesman.")
                raise err
        obj_value = {k: v for k, v in kwargs.items()
                     if k in self.model_cls.updatable_fields()}
        return super().create(salesman_id=salesman_id, **obj_value)
