from ee_crm.adapters.orm import start_mappers
from ee_crm.cli_interface.commands import cli
from ee_crm.cli_interface.views.view_errors import ErrorView
from ee_crm.exceptions import CRMException
from ee_crm.config import setup_file_logger


def main():
    logger = setup_file_logger(name=__name__, filename="ERRORS")

    try:
        start_mappers()
        cli()

    except CRMException as err:
        log_msg = f"{err.level} ::: {type(err).__name__} ::: {err}"
        if err.threat == "warning":
            logger.warning(log_msg)
        else:
            logger.error(log_msg)
        error = ErrorView(err)
        error.display_error()

    except Exception as err:
        log_msg = f"critical ::: {type(err).__name__} ::: {err}"
        logger.critical(log_msg)
        raise err


if __name__ == '__main__':
    main()
