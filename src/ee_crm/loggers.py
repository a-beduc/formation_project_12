"""Function to handle the configuration of loggers.

Functions
    setup_file_logger           # Prepare the logger
    init_sentry                 # Initialize sentry
    log_sentry_traceback        # Add traceback to sentry logs
    log_sentry_message_event    # Add information to the sentry logs
"""
import logging
from datetime import date
from pathlib import Path

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from ee_crm.config import get_local_log_dir, get_sentry_dsn


def _create_or_find_log_storage(filename=None):
    """Private helper for creating the path of the logger.

    Args
        filename(str|None): Name of the specific log file to create.

    Returns
        Path: Path to the log file.
    """
    log_path = f"{get_local_log_dir()}/{date.today()}_eecrm_{filename}.log"
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def setup_file_logger(name="default", filename="default"):
    """Prepare and set up the loggers.

    Args
        name(str): Name of the logger.
        filename(str): Name of the log file to create.

    Returns
        Logger: Configured local logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    log_path = _create_or_find_log_storage(filename)

    fh = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    formatter = logging.Formatter(
        "{asctime} - {name} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    fh.setFormatter(formatter)
    fh.setLevel(logging.INFO)
    logger.addHandler(fh)

    return logger


def init_sentry():
    """Initialize the sentry logger."""
    sentry_dsn = get_sentry_dsn()
    if not sentry_dsn:
        return

    # To stop sentry from sending local loggers
    stop_log = LoggingIntegration(
        level=None,
        event_level=None
    )

    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[stop_log],
        send_default_pii=True
    )


def log_sentry_traceback(error):
    """Catch the traceback and send it to sentry.

    Args
        error(Exception): Exception raised by the logger.
    """
    sentry_sdk.capture_exception(error)


def log_sentry_message_event(message, level, tags=None, extra=None, user=None):
    """

    Args
        message(str): Message to be logged.
        level(str): Logging level.
        tags(dict|None): Tags to add to the log.
        extra(dict|None): Extra information to be logged.
        user(str|None): User ID to be logged.
    """
    if tags:
        for k, v in tags.items():
            sentry_sdk.set_tag(k, v)

    if extra:
        for k, v in extra.items():
            sentry_sdk.set_extra(k, v)

    if user:
        sentry_sdk.set_user(user)

    sentry_sdk.capture_message(message, level=level)
