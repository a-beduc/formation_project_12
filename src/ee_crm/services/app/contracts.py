from ee_crm.domain.model import Contract, Role
from ee_crm.services.dto import ContractDTO, ClientDTO
from ee_crm.services.app.base import BaseService, ServiceError


class ContractServiceError(ServiceError):
    pass


class ContractService(BaseService):
    def __init__(self, uow):
        super().__init__(
            uow,
            Contract,
            ContractDTO,
            ContractServiceError,
            "contracts"
        )

    def create(self, client_id=None, total_amount=None):
        with self.uow:
            client = self.uow.clients.get(client_id)
            if not client:
                raise ContractServiceError(
                    "Contract must be linked to a client")
            if not client.salesman:
                raise ContractServiceError(
                    "Client must have a designated salesman")
            if not client.salesman.role == Role.SALES:
                raise ContractServiceError(
                    "Associated collaborator is not in SALES, "
                    "must reassign client"
                )

        return super().create(client_id=client_id, total_amount=total_amount)

    def sign_contract(self, contract_id):
        with self.uow:
            contract = self._repo.get(contract_id)
            contract.sign()
            self.uow.commit()

    def modify_total_amount(self, contract_id, total_amount):
        with self.uow:
            contract = self._repo.get(contract_id)
            contract.change_total_amount(total_amount)
            self.uow.commit()

    def pay_amount(self, contract_id, amount):
        with self.uow:
            contract = self._repo.get(contract_id)
            contract.register_payment(amount)
            self.uow.commit()

    def retrieve_associated_client(self, contract_id):
        with self.uow:
            contract = self._repo.get(contract_id)
            try:
                client = contract.client
                return (ClientDTO.from_domain(client),)
            except AttributeError:
                raise ContractServiceError("No associated client")
