from ee_crm.adapters.orm import start_mappers
from ee_crm.cli_interface.commands import cli
from ee_crm.cli_interface.views.view_errors import ErrorView
from ee_crm.exceptions import CRMException


def main():
    try:
        start_mappers()
        cli()
    except CRMException as err:
        error = ErrorView(err)
        error.display_error()


if __name__ == '__main__':
    main()
