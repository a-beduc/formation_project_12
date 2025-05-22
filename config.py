import os
from dotenv import load_dotenv
from pathlib import Path


load_dotenv()


def get_postgres_uri():
    user = os.getenv('PG_USER')
    password = os.getenv('PG_PASSWORD')
    host = os.getenv('PG_HOST')
    port = os.getenv('PG_PORT')
    dbname = os.getenv('PG_DBNAME')
    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"


def get_secret_key():
    return os.getenv('SECRET_KEY')


def get_token_store_path():
    return str(Path(__file__).resolve().parent / os.getenv('TOKEN_STORAGE'))


def get_token_access_lifetime():
    return int(os.getenv('ACCESS_LIFETIME'))


def get_token_refresh_lifetime():
    return int(os.getenv('REFRESH_LIFETIME'))
