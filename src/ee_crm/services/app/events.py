from ee_crm.domain.model import Event, Role
from ee_crm.exceptions import EventServiceError
from ee_crm.services.app.base import BaseService
from ee_crm.services.dto import EventDTO, ClientDTO


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
                err = EventServiceError(f"No contract found.")
                err.tips = (f"The contract_id {contract_id} isn't linked to a "
                            f"contract in the database.")
                raise err
            if not contract.signed:
                err = EventServiceError("Can't create event for unsigned "
                                        "contracts")
                err.tips = ("The contract linked to the event hasn't been "
                            "signed yet. It must be signed before an event "
                            "can be created.")
                raise err
        obj_value = {k: v for k, v in kwargs.items()
                     if k in self.model_cls.updatable_fields()}
        return super().create(contract_id=contract_id, **obj_value)

    def assign_support(self, event_id, supporter_id):
        with self.uow:
            supporter = self.uow.collaborators.get(supporter_id)
            if supporter is None:
                err = self.error_cls("Can't find collaborator")
                err.tips = (f"The supporter_id {supporter_id} isn't linked "
                            f"to a collaborator in the database.")
                raise err
            if supporter.role != Role.SUPPORT:
                err = self.error_cls("Can only assign supports to event")
                err.tips = (f"The supporter_id {supporter_id} isn't linked "
                            f"to a collaborator with the role SUPPORTER "
                            f"in the database.")
                raise err
            event = self._repo.get(event_id)
            event.supporter_id = supporter_id
            self.uow.commit()

    def retrieve_associated_client(self, event_id):
        with self.uow:
            event = self._repo.get(event_id)
            client = event.contract.client
            return (ClientDTO.from_domain(client),)
