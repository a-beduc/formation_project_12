"""CLI entrypoint for ee_crm.

Initialize the loggers, the ORM mappers and handle application specific
errors.

Function
    __main__    # CLI entrypoint function
"""
from ee_crm.adapters.orm import start_mappers
from ee_crm.cli_interface.commands import cli
from ee_crm.cli_interface.views.view_errors import ErrorView
from ee_crm.exceptions import CRMException
from ee_crm.loggers import init_sentry, log_sentry_traceback, setup_file_logger


init_sentry()


def main():
    """Run the ee_crm CLI entrypoint.

    Configure the logger, register the mappers, invoke the Click CLI,
    handle the errors.

    Raises
        Exception: Any uncatch exception raised.
    """
    logger = setup_file_logger(name=__name__, filename="ERRORS")

    try:
        start_mappers()
        cli()

    except CRMException as err:
        log_msg = (f"{err.level} ::: {type(err).__name__} ::: {err} ::: "
                   f"{err.tips}")
        if err.threat == "warning":
            logger.warning(log_msg)
        else:
            logger.error(log_msg)

        ErrorView(err).display_error()

        log_sentry_traceback(error=err)

    except Exception as err:
        log_msg = (f"critical ::: {type(err).__name__} ::: {err} ::: "
                   f"...")
        logger.critical(log_msg)

        log_sentry_traceback(error=err)
        raise err


if __name__ == '__main__':
    main()
