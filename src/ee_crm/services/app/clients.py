from ee_crm.domain.model import Client
from ee_crm.exceptions import ClientServiceError
from ee_crm.services.app.base import BaseService
from ee_crm.services.dto import ClientDTO


class ClientService(BaseService):
    def __init__(self, uow):
        super().__init__(
            uow,
            Client,
            ClientDTO,
            ClientServiceError,
            "clients"
        )

    def create(self, salesman_id=None, **kwargs):
        with self.uow:
            if self.uow.collaborators.get(salesman_id).role != 4:
                raise self.error_cls("Only sales people can create clients")
        obj_value = {k: v for k, v in kwargs.items()
                     if k in self.model_cls.updatable_fields()}
        return super().create(salesman_id=salesman_id, **obj_value)
