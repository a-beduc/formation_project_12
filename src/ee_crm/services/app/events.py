from ee_crm.domain.model import Event, Role
from ee_crm.services.app.base import BaseService, ServiceError
from ee_crm.services.dto import EventDTO


class EventServiceError(ServiceError):
    pass


class EventService(BaseService):
    def __init__(self, uow):
        super().__init__(
            uow,
            Event,
            EventDTO,
            EventServiceError,
            "events"
        )

    def create(self, contract_id=None, **kwargs):
        with self.uow:
            contract = self.uow.contracts.get(contract_id)
            if contract is None:
                raise EventServiceError(f"No contract found with id "
                                        f"{contract_id}")
            if not contract.signed:
                raise EventServiceError("Can't create event for unsigned "
                                        "contracts")
        obj_value = {k: v for k, v in kwargs.items()
                     if k in self.model_cls.updatable_fields()}
        return super().create(contract_id=contract_id, **obj_value)

    def assign_support(self, event_id, supporter_id):
        with self.uow:
            supporter = self.uow.collaborators.get(supporter_id)
            if supporter is None:
                raise self.error_cls("Can't find collaborator")
            if supporter.role != Role.SUPPORT:
                raise self.error_cls("Can only assign supports to event")
            event = self._repo.get(event_id)
            event.supporter_id = supporter_id
            self.uow.commit()
