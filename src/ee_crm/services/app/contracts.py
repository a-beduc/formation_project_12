from ee_crm.domain.model import Contract
from ee_crm.services.dto import ContractDTO
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
