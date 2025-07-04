import datetime
import json
import jwt
from pathlib import Path

from ee_crm.config import get_secret_key, get_token_store_path, \
    get_token_access_lifetime, get_token_refresh_lifetime
from ee_crm.exceptions import ExpiredToken, BadToken, NoToken, TokenError


def _now():
    return int(datetime.datetime.now().timestamp())


def _encode(payload):
    return jwt.encode(payload, get_secret_key(), algorithm='HS256')


def _decode(token, verify_exp=True):
    try:
        return jwt.decode(token, get_secret_key(), algorithms='HS256',
                          options={'verify_exp': verify_exp})
    except jwt.ExpiredSignatureError:
        err = ExpiredToken("Expired token")
        err.tips = "Your session expired, please try to log in again."
        raise err
    except jwt.InvalidTokenError:
        err = BadToken("Bad token")
        err.tips = ("The token signature isn't valid, please try to log in "
                    "again to refresh it")
        raise err


def _storage_path():
    path = Path(get_token_store_path())
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _read_storage():
    path = _storage_path()
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}


def _write_storage(access_token, refresh_token):
    path = _storage_path()
    content = {
        "access-token": access_token,
        "refresh-token": refresh_token,
    }
    with path.open("w", encoding="utf-8") as file:
        json.dump(content, file, indent=4)


def _wipe_storage():
    path = _storage_path()
    try:
        path.unlink()
    except FileNotFoundError:
        err = NoToken('No valid credentials, already logged out')
        err.tips = "You are already logged out. You can try to log in again."
        raise err


def _prepare_access_payload(data):
    iat = _now()
    exp = iat + get_token_access_lifetime()
    return {
        "sub": str(data["sub"]),
        "c_id": int(data["c_id"]),
        "role": int(data["role"]),
        "name": str(data["name"]),
        "iat": iat,
        "exp": exp
    }


def _prepare_refresh_payload(data):
    iat = _now()
    exp = iat + get_token_refresh_lifetime()
    return {
        "sub": str(data["sub"]),
        "iat": iat,
        "exp": exp
    }


def create_and_store_tokens(data):
    access_payload = _prepare_access_payload(data)
    refresh_payload = _prepare_refresh_payload(data)
    access_token = _encode(access_payload)
    refresh_token = _encode(refresh_payload)
    _write_storage(access_token, refresh_token)


def verify_token():
    tokens = _read_storage()
    access_token = tokens.get("access-token", None)
    if access_token is None:
        err = BadToken("No access token")
        err.tips = "No credentials found, please try to log in again."
        raise err

    try:
        return _decode(access_token)
    except ExpiredToken:
        pass

    refresh_token = tokens.get("refresh-token", None)
    if refresh_token is None:
        _wipe_storage()
        err = BadToken("Missing refresh token")
        err.tips = "The token is expired, please try to log in again."
        raise err

    try:
        _decode(refresh_token)
    except TokenError:
        _wipe_storage()
        err = BadToken("Invalid refresh token")
        err.tips = "The token is invalid, please try to log in again."
        raise err

    old_access_token_payload = _decode(access_token, verify_exp=False)
    new_access_token_payload = (
        _prepare_access_payload(old_access_token_payload))
    new_access_token = _encode(new_access_token_payload)

    _write_storage(new_access_token, refresh_token)
    return new_access_token_payload


def wipe_tokens():
    _wipe_storage()
