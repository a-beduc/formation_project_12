from domain.model import Client
from services.dto import ClientDTO
from services.app.base import BaseService, ServiceError


class ClientServiceError(ServiceError):
    pass


class ClientService(BaseService):
    def __init__(self, uow):
        super().__init__(
            uow,
            Client,
            ClientDTO,
            ClientServiceError,
            "clients"
        )

    def create(self, salesman_id, **kwargs):
        with self.uow:
            if self.uow.collaborators.get(salesman_id).role_id != 4:
                raise self.error_cls("Only sales people can create clients")
        return super().create(salesman_id=salesman_id, **kwargs)
