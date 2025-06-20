from datetime import date
from dotenv import load_dotenv
import logging
import os
from pathlib import Path


load_dotenv()


def get_postgres_uri():
    user = os.getenv('PG_USER')
    password = os.getenv('PG_PASSWORD')
    host = os.getenv('PG_HOST')
    port = os.getenv('PG_PORT')
    dbname = os.getenv('PG_DBNAME')
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{dbname}"


def get_secret_key():
    return os.getenv('SECRET_KEY')


def get_token_store_path():
    return str(Path(__file__).resolve().parent / os.getenv('TOKEN_STORAGE'))


def get_token_access_lifetime():
    return int(os.getenv('ACCESS_LIFETIME'))


def get_token_refresh_lifetime():
    return int(os.getenv('REFRESH_LIFETIME'))


def get_local_log_dir():
    return os.getenv('LOCAL_LOG_STORAGE')


def _create_or_find_log_storage(filename=None):
    log_path = f"{get_local_log_dir()}/{date.today()}_eecrm_{filename}.log"
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def setup_file_logger(name="default", filename="default"):
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
