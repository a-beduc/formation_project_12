"""Helpers functions for creating, persisting and validating JSON Web
Tokens (JWT) on the client side of the application.

Function
    create_and_store_tokens # Creates a new JWT token and store it.
    verify_token            # Decode a token and verify its validity.
    wipe_tokens             # Clear the storage directory of tokens

All other functions are private.
"""
import datetime
import json
from pathlib import Path

import jwt

from ee_crm.config import get_secret_key, get_token_store_path, \
    get_token_access_lifetime, get_token_refresh_lifetime
from ee_crm.exceptions import ExpiredToken, BadToken, NoToken, TokenError


def _now():
    """Returns the current UTC time as a timestamp.

    Returns
        int: Seconds since epoch.
    """
    return int(datetime.datetime.now().timestamp())


def _encode(payload):
    """Create a signed JWT.

    Args
        payload (dict): Payload of the JWT.

    Returns
        str: JWT string encoded with the supplied payload.
    """
    return jwt.encode(payload, get_secret_key(), algorithm='HS256')


def _decode(token, verify_exp=True):
    """Decode a JWT and return its payload.

    Args
        token (str): string encoded with the supplied payload.
        verify_exp (bool): If True, verify that the token is valid.

    Returns
        dict: Payload of the JWT.

    Raises
        ExpiredToken: If the token expired.
        BadToken: If the token is invalid, has been tampered with.
    """
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
    """Returns the storage path for storing tokens.

    Returns
        pathlib.Path: Absolute storage path.
    """
    path = Path(get_token_store_path())
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _read_storage():
    """Read tokens from storage path.

    Returns
        dict: {'access-token': str, 'refresh-token': str} if the file
            exists and is valid, otherwise empty dict.
    """
    path = _storage_path()
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}


def _write_storage(access_token, refresh_token):
    """Persists tokens at the storage path.

    Args:
        access_token (str): Access token.
        refresh_token (str): Refresh token.
    """
    path = _storage_path()
    content = {
        "access-token": access_token,
        "refresh-token": refresh_token,
    }
    with path.open("w", encoding="utf-8") as file:
        json.dump(content, file, indent=4)


def _wipe_storage():
    """Delete the local stored tokens.

    Raises:
        NoToken: If the store file does not exist.
    """
    path = _storage_path()
    try:
        path.unlink()
    except FileNotFoundError:
        err = NoToken('No valid credentials, already logged out')
        err.tips = "You are already logged out. You can try to log in again."
        raise err


def _prepare_access_payload(data):
    """Prepares access payload.

    Args
        data (dict): Payload of the JWT, expect at least the keys
            ["sub", "c_id", "role", "name"].

    Returns
        dict: Payload of the JWT.
    """
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
    """Prepares refresh payload.

    Args
        data (dict): Payload of the JWT, expect at least the keys
            ["sub"]

    Returns
        dict: Payload of the JWT.
    """
    iat = _now()
    exp = iat + get_token_refresh_lifetime()
    return {
        "sub": str(data["sub"]),
        "iat": iat,
        "exp": exp
    }


def create_and_store_tokens(data):
    """Creates and persists JWT access and refresh tokens.

    Args
        data (dict): Payload of the JWTs.
    """
    access_payload = _prepare_access_payload(data)
    refresh_payload = _prepare_refresh_payload(data)
    access_token = _encode(access_payload)
    refresh_token = _encode(refresh_payload)
    _write_storage(access_token, refresh_token)


def verify_token():
    """Return the stored access token payload, refresh it if necessary.

    Returns
        dict: Payload of the JWT access token.

    Raises
        BadToken: If any problems occurs.
    """
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
    """Delete the local stored tokens."""
    _wipe_storage()
