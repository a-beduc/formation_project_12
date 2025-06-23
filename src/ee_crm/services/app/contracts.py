from ee_crm.domain.model import Contract, Role
from ee_crm.exceptions import ContractServiceError
from ee_crm.services.app.base import BaseService
from ee_crm.services.dto import ContractDTO, ClientDTO


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
                err = ContractServiceError(
                    "Contract must be linked to a client")
                err.tips = (f"The client_id {client_id} isn't linked to a "
                            f"client in the database.")
                raise err
            if not client.salesman:
                err = ContractServiceError(
                    "Client must have a designated salesman")
                err.tips = (f"The client with the pk {client_id} doesn't have"
                            f"a designated salesman. Provide him/her one to"
                            f"be able to create contracts for him/her")
                raise err
            if not client.salesman.role == Role.SALES:
                err = ContractServiceError(
                    "Associated collaborator is not in SALES, "
                    "must reassign client")
                err.tips = ("The collaborator associated with the client of "
                            "this contract is not a salesman, contact a "
                            "member of the MANAGEMENT to resolve this issue.")
                raise err

        return super().create(client_id=client_id, total_amount=total_amount)

    def sign_contract(self, contract_id):
        with self.uow:
            contract = self._repo.get(contract_id)
            if contract.signed:
                err = ContractServiceError("This contract is already signed")
                err.threat = "warning"
                err.tips = ("This contract is already signed. "
                            "It can't be unsigned or signed again.")
                raise err
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
                err = ContractServiceError("No associated client")
                err.tips = (f"The contract_id {contract_id} isn't linked to a "
                            f"client in the database.")
                raise err
