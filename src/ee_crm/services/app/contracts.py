"""Service layer responsible for Contract domain entities.

Classes
    ContractService # Business operations for contracts.
"""
from ee_crm.domain.model import Contract, Role
from ee_crm.exceptions import ContractServiceError
from ee_crm.services.app.base import BaseService
from ee_crm.services.dto import ContractDTO


class ContractService(BaseService):
    """Manage contracts business operations.

    Attributes
        uow (AbstractUnitOfWork): Unit of work exposing repositories.
    """
    def __init__(self, uow):
        super().__init__(
            uow,
            Contract,
            ContractDTO,
            ContractServiceError,
            "contracts"
        )

    def create(self, client_id=None, total_amount=None):
        """Create a contract for an existing client.

        Args
            client_id (int): Primary key of the client.
            total_amount (int|float): Total value of the contract.

        Returns
            Tuple[ContractDTO]: Contract dto for the newly created
                contract entity.

        Raises
            ContractServiceError: If no client is found with given
                parameters, the given client does not have a dedicated
                salesman, the current assigned collaborator does not
                have the SALES role.
        """
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
        """Sign a contract.

        Args
            contract_id (int): Primary key of the contract.

        Raises
            ContractServiceError: If the contract is already signed.
        """
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
        """Update the total amount of the contract.

        Args
            contract_id (int): Primary key of the contract.
            total_amount (int|float): New total value of the contract.
        """
        with self.uow:
            contract = self._repo.get(contract_id)
            contract.change_total_amount(total_amount)
            self.uow.commit()

    def pay_amount(self, contract_id, amount):
        """Pay a certain amount of a contract value.

        Args
            contract_id (int): Primary key of the contract.
            amount (int|float): Payment value.
        """
        with self.uow:
            contract = self._repo.get(contract_id)
            contract.register_payment(amount)
            self.uow.commit()

    def retrieve_collaborator_contracts(self,
                                        collaborator_id,
                                        only_unpaid=False,
                                        only_unsigned=False,
                                        only_no_event=False,
                                        sort=None, **kwargs):
        """Retrieve contracts associated with collaborator.

        Args
            collaborator_id (int): Primary key of the collaborator.
            only_unpaid (bool): If True, only unpaid contracts are
                returned.
            only_unsigned (bool): If True, only unsigned contracts are
                returned.
            only_no_event (bool): If True, only contracts without linked
                events are returned.
            sort (Iterable(Tuple(str, bool)): An iterable to apply an
                optional sorting to the queries made to the persistence
                layer.
            **kwargs (Any): Keyword arguments used to filter entities.

        Returns
            Tuple[ContractDTO]: A tuple containing the contracts
                associated the given collaborator.
        """
        filters = {k: v for k, v in kwargs.items()
                   if k in self.model_cls.filterable_fields()}
        with self.uow:
            contracts = self._repo.get_contracts_collaborator(
                collaborator_id,
                only_unpaid=only_unpaid,
                only_unsigned=only_unsigned,
                only_no_event=only_no_event,
                sort=sort, **filters)
            return tuple([self.dto_cls.from_domain(c) for c in contracts])
