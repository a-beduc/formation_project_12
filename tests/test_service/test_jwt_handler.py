import datetime
import json

import pytest

from ee_crm.services.auth import jwt_handler


# 2025-01-01 01:01:01
FAKE_TIME = datetime.datetime(2025, 1, 1, 1, 1, 1)
ACCESS_LIFETIME = 30
REFRESH_LIFETIME = 300
SECRET_KEY = 'mysecretkeyissupersecretandnooneknowsit'


@pytest.fixture
def patch_lifetimes(mocker):
    mocker.patch.object(jwt_handler, "get_token_access_lifetime",
                        return_value=ACCESS_LIFETIME)
    mocker.patch.object(jwt_handler, "get_token_refresh_lifetime",
                        return_value=REFRESH_LIFETIME)


@pytest.fixture
def patch_past_time(mocker, patch_lifetimes):
    mocker.patch.object(jwt_handler, "_now",
                        return_value=int(FAKE_TIME.timestamp()))


@pytest.fixture
def patch_storage(tmp_path, mocker):
    storage = tmp_path / "tokens.json"
    mocker.patch.object(jwt_handler, 'get_token_store_path',
                        return_value=str(storage))
    return storage


@pytest.fixture
def patch_secret(mocker):
    mocker.patch.object(jwt_handler, 'get_secret_key',
                        return_value=SECRET_KEY)


def make_tokens(data, access_expired=False, refresh_expired=False):
    access_payload = jwt_handler._prepare_access_payload(data)
    if access_expired:
        access_payload['exp'] -= 2 * ACCESS_LIFETIME
    refresh_payload = jwt_handler._prepare_refresh_payload(data)
    if refresh_expired:
        refresh_payload['exp'] -= 2 * REFRESH_LIFETIME
    access = jwt_handler._encode(access_payload)
    refresh = jwt_handler._encode(refresh_payload)
    return access, refresh, access_payload


def test_prepare_access_payload(patch_past_time):
    expected_payload = {
        "sub": "Bob",
        "c_id": 3,
        "role": 2,
        "name": "test_fn test_ln",
        "iat": int(FAKE_TIME.timestamp()),
        "exp": int(FAKE_TIME.timestamp() + ACCESS_LIFETIME)
    }
    data = {
        "sub": "Bob",
        "c_id": 3,
        "role": 2,
        "name": "test_fn test_ln",
    }
    assert jwt_handler._prepare_access_payload(data) == expected_payload


def test_prepare_refresh_payload(patch_past_time):
    expected_payload = {
        "sub": "Bob",
        "iat": int(FAKE_TIME.timestamp()),
        "exp": int(FAKE_TIME.timestamp() + REFRESH_LIFETIME)
    }
    data = {
        "sub": "Bob",
        "c_id": 3,
        "role": 2,
        "name": "test_fn test_ln",
    }
    assert jwt_handler._prepare_refresh_payload(data) == expected_payload


def test_decode_expired_token_raise_expired_exception(patch_past_time,
                                                      patch_secret):
    expired_token = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJCb2IiLCJ"
                     "uYW1lIjoidGVzdF9mbiB0ZXN0X2xuIiwicm9sZSI6MiwiaWF0IjoxNzQ"
                     "4MDAxODAsImV4cCI6MTc0ODAwNDgwfQ.1BEJRpkrixadkr-M2zOAl3ol"
                     "8NChcVv1A1-AYepo5-I")

    with pytest.raises(jwt_handler.ExpiredToken, match="Expired token"):
        jwt_handler._decode(expired_token)


def test_decode_expired_token_without_verify_exp_return_payload(
        patch_past_time, patch_secret):
    expired_token = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJCb2IiLCJ"
                     "uYW1lIjoidGVzdF9mbiB0ZXN0X2xuIiwicm9sZSI6MiwiaWF0IjoxNzQ"
                     "4MDAxODAsImV4cCI6MTc0ODAwNDgwfQ.1BEJRpkrixadkr-M2zOAl3ol"
                     "8NChcVv1A1-AYepo5-I")
    payload = jwt_handler._decode(expired_token, verify_exp=False)
    assert payload == {"sub": "Bob",
                       "name": "test_fn test_ln",
                       "role": 2,
                       "iat": 174800180,
                       "exp": 174800480}


def test_decode_modified_token_raise_bad_exception(patch_past_time,
                                                   patch_secret):
    bad_token = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJCb2IiLCJuYW"
                 "1lIjoidGVzdF9mbiB0ZXN0X2xuIiwicm9sZSI6MiwiaWF0IjoxNzQ4MTYxO"
                 "DAxLCJleHAiOjE3NDgxNjQ4MDF9.C1cH9ACmsW9q4Yp5h9SBgbMBySH19JV"
                 "_eXVXNUD3nU")
    with pytest.raises(jwt_handler.BadToken, match="Bad token"):
        jwt_handler._decode(bad_token)


def test_create_and_store_tokens(mocker, patch_past_time, patch_storage,
                                 patch_secret):
    data = {
        "sub": "username",
        "c_id": 5,
        "role": 1,
        "name": "Bob ross"
    }

    spy_storage = mocker.spy(jwt_handler, '_write_storage')
    spy_encode = mocker.spy(jwt_handler, '_encode')

    jwt_handler.create_and_store_tokens(data)

    assert spy_storage.call_count == 1
    assert spy_encode.call_count == 2

    assert patch_storage.exists()

    with patch_storage.open() as file:
        content = json.load(file)

    assert (jwt_handler._decode(content["access-token"], verify_exp=False) ==
            jwt_handler._prepare_access_payload(data))


def test_verify_token_happy_path(mocker, patch_secret, patch_lifetimes):
    storage = {}
    mocker.patch.object(jwt_handler, "_wipe_storage", return_value={})
    mocker.patch.object(jwt_handler, "_read_storage", return_value=storage)

    data = {
        "sub": "username",
        "c_id": 5,
        "role": 1,
        "name": "Bob ross"
    }
    access, refresh, access_payload = make_tokens(data)

    storage.update({'access-token': access, 'refresh-token': refresh})

    spy_decode = mocker.spy(jwt_handler, '_decode')

    payload = jwt_handler.verify_token()

    assert payload == access_payload
    assert spy_decode.call_count == 1


def test_verify_token_access_expired_refresh_ok(mocker, patch_secret,
                                                patch_lifetimes):
    storage = {}
    mocker.patch.object(jwt_handler, "_wipe_storage", return_value={})
    mocker.patch.object(jwt_handler, "_read_storage", return_value=storage)

    data = {
        "sub": "username",
        "c_id": 5,
        "role": 1,
        "name": "Bob ross"
    }
    access, refresh, _ = make_tokens(data, access_expired=True)

    storage.update({'access-token': access, 'refresh-token': refresh})

    spy_decode = mocker.spy(jwt_handler, '_decode')

    payload = jwt_handler.verify_token()
    payload = {k: v for k, v in payload.items() if k not in ["exp", "iat"]}

    assert data == payload
    assert spy_decode.call_count == 3


def test_verify_token_access_expired_refresh_expired(mocker, patch_secret,
                                                     patch_lifetimes):
    storage = {}
    mocker.patch.object(jwt_handler, "_wipe_storage", return_value={})
    mocker.patch.object(jwt_handler, "_read_storage", return_value=storage)

    data = {
        "sub": "username",
        "c_id": 5,
        "role": 1,
        "name": "Bob ross"
    }
    access, refresh, _ = make_tokens(data, access_expired=True,
                                     refresh_expired=True)

    storage.update({'access-token': access, 'refresh-token': refresh})

    spy_decode = mocker.spy(jwt_handler, '_decode')

    with pytest.raises(jwt_handler.BadToken, match="Invalid refresh token"):
        jwt_handler.verify_token()

    assert spy_decode.call_count == 2


def test_verify_token_access_bad(mocker, patch_secret, patch_lifetimes):
    storage = {}
    mocker.patch.object(jwt_handler, "_wipe_storage", return_value={})
    mocker.patch.object(jwt_handler, "_read_storage", return_value=storage)

    data = {
        "sub": "username",
        "c_id": 5,
        "role": 1,
        "name": "Bob ross"
    }
    access, refresh, _ = make_tokens(data)

    storage.update({'access-token': f"{access}modifiedsignature",
                    'refresh-token': refresh})

    spy_decode = mocker.spy(jwt_handler, '_decode')

    with pytest.raises(jwt_handler.BadToken, match="Bad token"):
        jwt_handler.verify_token()

    assert spy_decode.call_count == 1


def test_verify_token_access_expired_refresh_bad(mocker, patch_secret,
                                                 patch_lifetimes):
    storage = {}
    mocker.patch.object(jwt_handler, "_wipe_storage", return_value={})
    mocker.patch.object(jwt_handler, "_read_storage", return_value=storage)

    data = {
        "sub": "username",
        "c_id": 5,
        "role": 1,
        "name": "Bob ross"
    }
    access, refresh, _ = make_tokens(data, access_expired=True)

    storage.update({'access-token': access,
                    'refresh-token': f"{refresh}modifiedsignature"})

    spy_decode = mocker.spy(jwt_handler, '_decode')

    with pytest.raises(jwt_handler.BadToken, match="Invalid refresh token"):
        jwt_handler.verify_token()

    assert spy_decode.call_count == 2


def test_verify_token_access_missing(mocker, patch_secret, patch_lifetimes):
    storage = {}
    mocker.patch.object(jwt_handler, "_wipe_storage", return_value={})
    mocker.patch.object(jwt_handler, "_read_storage", return_value=storage)

    with pytest.raises(jwt_handler.BadToken, match="No access token"):
        jwt_handler.verify_token()
