"""Helpers functions that prepare environment variables and settings.

Function
    get_postgre_uri             # construct postgre uri
    get_secret_key              # retrieve secret key
    get_token_store_path        # construct store absolute path
    get_token_access_lifetime   # retrieve jwt access lifetime
    get_token_refresh_lifetime  # retrieve jwt refresh lifetime
    get_sentry_dsn              # retrieve sentry dsn url
    get_local_log_dir           # construct local log dir
"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def get_postgres_uri():
    """Helper that retrieve env variables and prepare the uri for the
    postgres database.

    Returns
        str: postgres uri.
    """
    user = os.getenv('PG_USER')
    password = os.getenv('PG_PASSWORD')
    host = os.getenv('PG_HOST')
    port = os.getenv('PG_PORT')
    dbname = os.getenv('PG_DBNAME')
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{dbname}"


def get_secret_key():
    """Helper that get the secret key from the environment variables.

    Returns
        str: secret key.
    """
    return os.getenv('SECRET_KEY')


def get_token_store_path():
    """Helper that prepare the absolute path for the token storing.

    Returns
        str: absolute path.
    """
    return str(Path(__file__).resolve().parent / os.getenv('TOKEN_STORAGE'))


def get_token_access_lifetime():
    """Helper that retrieve the token access lifetime from the
    environment variables.

    Returns
        int: token access lifetime (seconds).
    """
    return int(os.getenv('ACCESS_LIFETIME'))


def get_token_refresh_lifetime():
    """Helper that retrieve the token refresh lifetime from the
    environment variables.

    Returns
        int: token refresh lifetime (seconds).
    """
    return int(os.getenv('REFRESH_LIFETIME'))


def get_sentry_dsn():
    """Helper that retrieve the sentry dsn url from the environment
    variables.

    Returns
        str: sentry dsn url.
    """
    return os.getenv('SENTRY_DSN')


def get_local_log_dir():
    """Helper that retrieve the absolute path for the local log.

    Returns
        str: absolute path.
    """
    return str(Path(__file__).resolve().parent /
               os.getenv('LOCAL_LOG_STORAGE'))
