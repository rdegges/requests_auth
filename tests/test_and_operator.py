import datetime

from responses import RequestsMock
import requests

import requests_auth
from requests_auth.testing import BrowserMock, create_token, token_cache, browser_mock
from tests.auth_helper import get_header


def test_basic_and_api_key_authentication_can_be_combined(responses: RequestsMock):
    basic_auth = requests_auth.Basic("test_user", "test_pwd")
    api_key_auth = requests_auth.HeaderApiKey("my_provided_api_key")
    header = get_header(responses, basic_auth & api_key_auth)
    assert header.get("Authorization") == "Basic dGVzdF91c2VyOnRlc3RfcHdk"
    assert header.get("X-Api-Key") == "my_provided_api_key"


def test_header_api_key_and_multiple_authentication_can_be_combined(
    token_cache, responses: RequestsMock
):
    api_key_auth = requests_auth.HeaderApiKey("my_provided_api_key")
    api_key_auth2 = requests_auth.HeaderApiKey(
        "my_provided_api_key2", header_name="X-Api-Key2"
    )
    api_key_auth3 = requests_auth.HeaderApiKey(
        "my_provided_api_key3", header_name="X-Api-Key3"
    )
    header = get_header(responses, api_key_auth & (api_key_auth2 & api_key_auth3))
    assert header.get("X-Api-Key") == "my_provided_api_key"
    assert header.get("X-Api-Key2") == "my_provided_api_key2"
    assert header.get("X-Api-Key3") == "my_provided_api_key3"


def test_multiple_auth_and_header_api_key_can_be_combined(
    token_cache, responses: RequestsMock
):
    api_key_auth = requests_auth.HeaderApiKey("my_provided_api_key")
    api_key_auth2 = requests_auth.HeaderApiKey(
        "my_provided_api_key2", header_name="X-Api-Key2"
    )
    api_key_auth3 = requests_auth.HeaderApiKey(
        "my_provided_api_key3", header_name="X-Api-Key3"
    )
    header = get_header(responses, (api_key_auth & api_key_auth2) & api_key_auth3)
    assert header.get("X-Api-Key") == "my_provided_api_key"
    assert header.get("X-Api-Key2") == "my_provided_api_key2"
    assert header.get("X-Api-Key3") == "my_provided_api_key3"


def test_multiple_auth_and_multiple_auth_can_be_combined(
    token_cache, responses: RequestsMock
):
    api_key_auth = requests_auth.HeaderApiKey("my_provided_api_key")
    api_key_auth2 = requests_auth.HeaderApiKey(
        "my_provided_api_key2", header_name="X-Api-Key2"
    )
    api_key_auth3 = requests_auth.HeaderApiKey(
        "my_provided_api_key3", header_name="X-Api-Key3"
    )
    api_key_auth4 = requests_auth.HeaderApiKey(
        "my_provided_api_key4", header_name="X-Api-Key4"
    )
    header = get_header(
        responses, (api_key_auth & api_key_auth2) & (api_key_auth3 & api_key_auth4)
    )
    assert header.get("X-Api-Key") == "my_provided_api_key"
    assert header.get("X-Api-Key2") == "my_provided_api_key2"
    assert header.get("X-Api-Key3") == "my_provided_api_key3"
    assert header.get("X-Api-Key4") == "my_provided_api_key4"


def test_basic_and_multiple_authentication_can_be_combined(
    token_cache, responses: RequestsMock
):
    basic_auth = requests_auth.Basic("test_user", "test_pwd")
    api_key_auth2 = requests_auth.HeaderApiKey(
        "my_provided_api_key2", header_name="X-Api-Key2"
    )
    api_key_auth3 = requests_auth.HeaderApiKey(
        "my_provided_api_key3", header_name="X-Api-Key3"
    )
    header = get_header(responses, basic_auth & (api_key_auth2 & api_key_auth3))
    assert header.get("Authorization") == "Basic dGVzdF91c2VyOnRlc3RfcHdk"
    assert header.get("X-Api-Key2") == "my_provided_api_key2"
    assert header.get("X-Api-Key3") == "my_provided_api_key3"


def test_query_api_key_and_multiple_authentication_can_be_combined(
    token_cache, responses: RequestsMock
):
    api_key_auth = requests_auth.QueryApiKey("my_provided_api_key")
    api_key_auth2 = requests_auth.QueryApiKey(
        "my_provided_api_key2", query_parameter_name="api_key2"
    )
    api_key_auth3 = requests_auth.HeaderApiKey(
        "my_provided_api_key3", header_name="X-Api-Key3"
    )

    # Mock a dummy response
    responses.add(responses.GET, "http://authorized_only")
    # Send a request to this dummy URL with authentication
    response = requests.get(
        "http://authorized_only", auth=api_key_auth & (api_key_auth2 & api_key_auth3)
    )
    # Return headers received on this dummy URL
    assert (
        response.request.path_url
        == "/?api_key=my_provided_api_key&api_key2=my_provided_api_key2"
    )
    assert response.request.headers.get("X-Api-Key3") == "my_provided_api_key3"


def test_oauth2_resource_owner_password_and_api_key_authentication_can_be_combined(
    token_cache, responses: RequestsMock
):
    resource_owner_password_auth = requests_auth.OAuth2ResourceOwnerPasswordCredentials(
        "http://provide_access_token", username="test_user", password="test_pwd"
    )
    responses.add(
        responses.POST,
        "http://provide_access_token",
        json={
            "access_token": "2YotnFZFEjr1zCsicMWpAA",
            "token_type": "example",
            "expires_in": 3600,
            "refresh_token": "tGzv3JOkF0XG5Qx2TlKWIA",
            "example_parameter": "example_value",
        },
    )
    api_key_auth = requests_auth.HeaderApiKey("my_provided_api_key")
    header = get_header(responses, resource_owner_password_auth & api_key_auth)
    assert header.get("Authorization") == "Bearer 2YotnFZFEjr1zCsicMWpAA"
    assert header.get("X-Api-Key") == "my_provided_api_key"


def test_oauth2_resource_owner_password_and_multiple_authentication_can_be_combined(
    token_cache, responses: RequestsMock
):
    resource_owner_password_auth = requests_auth.OAuth2ResourceOwnerPasswordCredentials(
        "http://provide_access_token", username="test_user", password="test_pwd"
    )
    responses.add(
        responses.POST,
        "http://provide_access_token",
        json={
            "access_token": "2YotnFZFEjr1zCsicMWpAA",
            "token_type": "example",
            "expires_in": 3600,
            "refresh_token": "tGzv3JOkF0XG5Qx2TlKWIA",
            "example_parameter": "example_value",
        },
    )
    api_key_auth = requests_auth.HeaderApiKey("my_provided_api_key")
    api_key_auth2 = requests_auth.HeaderApiKey(
        "my_provided_api_key2", header_name="X-Api-Key2"
    )
    header = get_header(
        responses, resource_owner_password_auth & (api_key_auth & api_key_auth2)
    )
    assert header.get("Authorization") == "Bearer 2YotnFZFEjr1zCsicMWpAA"
    assert header.get("X-Api-Key") == "my_provided_api_key"
    assert header.get("X-Api-Key2") == "my_provided_api_key2"


def test_oauth2_client_credential_and_api_key_authentication_can_be_combined(
    token_cache, responses: RequestsMock
):
    resource_owner_password_auth = requests_auth.OAuth2ClientCredentials(
        "http://provide_access_token", client_id="test_user", client_secret="test_pwd"
    )
    responses.add(
        responses.POST,
        "http://provide_access_token",
        json={
            "access_token": "2YotnFZFEjr1zCsicMWpAA",
            "token_type": "example",
            "expires_in": 3600,
            "refresh_token": "tGzv3JOkF0XG5Qx2TlKWIA",
            "example_parameter": "example_value",
        },
    )
    api_key_auth = requests_auth.HeaderApiKey("my_provided_api_key")
    header = get_header(responses, resource_owner_password_auth & api_key_auth)
    assert header.get("Authorization") == "Bearer 2YotnFZFEjr1zCsicMWpAA"
    assert header.get("X-Api-Key") == "my_provided_api_key"


def test_oauth2_client_credential_and_multiple_authentication_can_be_combined(
    token_cache, responses: RequestsMock
):
    resource_owner_password_auth = requests_auth.OAuth2ClientCredentials(
        "http://provide_access_token", client_id="test_user", client_secret="test_pwd"
    )
    responses.add(
        responses.POST,
        "http://provide_access_token",
        json={
            "access_token": "2YotnFZFEjr1zCsicMWpAA",
            "token_type": "example",
            "expires_in": 3600,
            "refresh_token": "tGzv3JOkF0XG5Qx2TlKWIA",
            "example_parameter": "example_value",
        },
    )
    api_key_auth = requests_auth.HeaderApiKey("my_provided_api_key")
    api_key_auth2 = requests_auth.HeaderApiKey(
        "my_provided_api_key2", header_name="X-Api-Key2"
    )
    header = get_header(
        responses, resource_owner_password_auth & (api_key_auth & api_key_auth2)
    )
    assert header.get("Authorization") == "Bearer 2YotnFZFEjr1zCsicMWpAA"
    assert header.get("X-Api-Key") == "my_provided_api_key"
    assert header.get("X-Api-Key2") == "my_provided_api_key2"


def test_oauth2_authorization_code_and_api_key_authentication_can_be_combined(
    token_cache, responses: RequestsMock, browser_mock: BrowserMock
):
    authorization_code_auth = requests_auth.OAuth2AuthorizationCode(
        "http://provide_code", "http://provide_access_token"
    )
    tab = browser_mock.add_response(
        opened_url="http://provide_code?response_type=code&state=163f0455b3e9cad3ca04254e5a0169553100d3aa0756c7964d897da316a695ffed5b4f46ef305094fd0a88cfe4b55ff257652015e4aa8f87b97513dba440f8de&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2F",
        reply_url="http://localhost:5000#code=SplxlOBeZQQYbYS6WxSbIA&state=163f0455b3e9cad3ca04254e5a0169553100d3aa0756c7964d897da316a695ffed5b4f46ef305094fd0a88cfe4b55ff257652015e4aa8f87b97513dba440f8de",
    )
    responses.add(
        responses.POST,
        "http://provide_access_token",
        json={
            "access_token": "2YotnFZFEjr1zCsicMWpAA",
            "token_type": "example",
            "expires_in": 3600,
            "refresh_token": "tGzv3JOkF0XG5Qx2TlKWIA",
            "example_parameter": "example_value",
        },
    )
    api_key_auth = requests_auth.HeaderApiKey("my_provided_api_key")
    header = get_header(responses, authorization_code_auth & api_key_auth)
    assert header.get("Authorization") == "Bearer 2YotnFZFEjr1zCsicMWpAA"
    assert header.get("X-Api-Key") == "my_provided_api_key"
    tab.assert_success(
        "You are now authenticated on 163f0455b3e9cad3ca04254e5a0169553100d3aa0756c7964d897da316a695ffed5b4f46ef305094fd0a88cfe4b55ff257652015e4aa8f87b97513dba440f8de. You may close this tab."
    )


def test_oauth2_authorization_code_and_multiple_authentication_can_be_combined(
    token_cache, responses: RequestsMock, browser_mock: BrowserMock
):
    authorization_code_auth = requests_auth.OAuth2AuthorizationCode(
        "http://provide_code", "http://provide_access_token"
    )
    tab = browser_mock.add_response(
        opened_url="http://provide_code?response_type=code&state=163f0455b3e9cad3ca04254e5a0169553100d3aa0756c7964d897da316a695ffed5b4f46ef305094fd0a88cfe4b55ff257652015e4aa8f87b97513dba440f8de&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2F",
        reply_url="http://localhost:5000#code=SplxlOBeZQQYbYS6WxSbIA&state=163f0455b3e9cad3ca04254e5a0169553100d3aa0756c7964d897da316a695ffed5b4f46ef305094fd0a88cfe4b55ff257652015e4aa8f87b97513dba440f8de",
    )
    responses.add(
        responses.POST,
        "http://provide_access_token",
        json={
            "access_token": "2YotnFZFEjr1zCsicMWpAA",
            "token_type": "example",
            "expires_in": 3600,
            "refresh_token": "tGzv3JOkF0XG5Qx2TlKWIA",
            "example_parameter": "example_value",
        },
    )
    api_key_auth = requests_auth.HeaderApiKey("my_provided_api_key")
    api_key_auth2 = requests_auth.HeaderApiKey(
        "my_provided_api_key2", header_name="X-Api-Key2"
    )
    header = get_header(
        responses, authorization_code_auth & (api_key_auth & api_key_auth2)
    )
    assert header.get("Authorization") == "Bearer 2YotnFZFEjr1zCsicMWpAA"
    assert header.get("X-Api-Key") == "my_provided_api_key"
    assert header.get("X-Api-Key2") == "my_provided_api_key2"
    tab.assert_success(
        "You are now authenticated on 163f0455b3e9cad3ca04254e5a0169553100d3aa0756c7964d897da316a695ffed5b4f46ef305094fd0a88cfe4b55ff257652015e4aa8f87b97513dba440f8de. You may close this tab."
    )


def test_oauth2_pkce_and_api_key_authentication_can_be_combined(
    token_cache, responses: RequestsMock, browser_mock: BrowserMock, monkeypatch
):
    monkeypatch.setattr(requests_auth.authentication.os, "urandom", lambda x: b"1" * 63)
    pkce_auth = requests_auth.OAuth2AuthorizationCodePKCE(
        "http://provide_code", "http://provide_access_token"
    )
    tab = browser_mock.add_response(
        opened_url="http://provide_code?response_type=code&state=163f0455b3e9cad3ca04254e5a0169553100d3aa0756c7964d897da316a695ffed5b4f46ef305094fd0a88cfe4b55ff257652015e4aa8f87b97513dba440f8de&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2F&code_challenge=5C_ph_KZ3DstYUc965SiqmKAA-ShvKF4Ut7daKd3fjc&code_challenge_method=S256",
        reply_url="http://localhost:5000#code=SplxlOBeZQQYbYS6WxSbIA&state=163f0455b3e9cad3ca04254e5a0169553100d3aa0756c7964d897da316a695ffed5b4f46ef305094fd0a88cfe4b55ff257652015e4aa8f87b97513dba440f8de",
    )
    responses.add(
        responses.POST,
        "http://provide_access_token",
        json={
            "access_token": "2YotnFZFEjr1zCsicMWpAA",
            "token_type": "example",
            "expires_in": 3600,
            "refresh_token": "tGzv3JOkF0XG5Qx2TlKWIA",
            "example_parameter": "example_value",
        },
    )
    api_key_auth = requests_auth.HeaderApiKey("my_provided_api_key")
    header = get_header(responses, pkce_auth & api_key_auth)
    assert header.get("Authorization") == "Bearer 2YotnFZFEjr1zCsicMWpAA"
    assert header.get("X-Api-Key") == "my_provided_api_key"
    tab.assert_success(
        "You are now authenticated on 163f0455b3e9cad3ca04254e5a0169553100d3aa0756c7964d897da316a695ffed5b4f46ef305094fd0a88cfe4b55ff257652015e4aa8f87b97513dba440f8de. You may close this tab."
    )


def test_oauth2_pkce_and_multiple_authentication_can_be_combined(
    token_cache, responses: RequestsMock, browser_mock: BrowserMock, monkeypatch
):
    monkeypatch.setattr(requests_auth.authentication.os, "urandom", lambda x: b"1" * 63)
    pkce_auth = requests_auth.OAuth2AuthorizationCodePKCE(
        "http://provide_code", "http://provide_access_token"
    )
    tab = browser_mock.add_response(
        opened_url="http://provide_code?response_type=code&state=163f0455b3e9cad3ca04254e5a0169553100d3aa0756c7964d897da316a695ffed5b4f46ef305094fd0a88cfe4b55ff257652015e4aa8f87b97513dba440f8de&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2F&code_challenge=5C_ph_KZ3DstYUc965SiqmKAA-ShvKF4Ut7daKd3fjc&code_challenge_method=S256",
        reply_url="http://localhost:5000#code=SplxlOBeZQQYbYS6WxSbIA&state=163f0455b3e9cad3ca04254e5a0169553100d3aa0756c7964d897da316a695ffed5b4f46ef305094fd0a88cfe4b55ff257652015e4aa8f87b97513dba440f8de",
    )
    responses.add(
        responses.POST,
        "http://provide_access_token",
        json={
            "access_token": "2YotnFZFEjr1zCsicMWpAA",
            "token_type": "example",
            "expires_in": 3600,
            "refresh_token": "tGzv3JOkF0XG5Qx2TlKWIA",
            "example_parameter": "example_value",
        },
    )
    api_key_auth = requests_auth.HeaderApiKey("my_provided_api_key")
    api_key_auth2 = requests_auth.HeaderApiKey(
        "my_provided_api_key2", header_name="X-Api-Key2"
    )
    header = get_header(responses, pkce_auth & (api_key_auth & api_key_auth2))
    assert header.get("Authorization") == "Bearer 2YotnFZFEjr1zCsicMWpAA"
    assert header.get("X-Api-Key") == "my_provided_api_key"
    assert header.get("X-Api-Key2") == "my_provided_api_key2"
    tab.assert_success(
        "You are now authenticated on 163f0455b3e9cad3ca04254e5a0169553100d3aa0756c7964d897da316a695ffed5b4f46ef305094fd0a88cfe4b55ff257652015e4aa8f87b97513dba440f8de. You may close this tab."
    )


def test_oauth2_implicit_and_api_key_authentication_can_be_combined(
    token_cache, responses: RequestsMock, browser_mock: BrowserMock
):
    implicit_auth = requests_auth.OAuth2Implicit("http://provide_token")
    expiry_in_1_hour = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    token = create_token(expiry_in_1_hour)
    tab = browser_mock.add_response(
        opened_url="http://provide_token?response_type=token&state=42a85b271b7a652ca3cc4c398cfd3f01b9ad36bf9c945ba823b023e8f8b95c4638576a0e3dcc96838b838bec33ec6c0ee2609d62ed82480b3b8114ca494c0521&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2F",
        reply_url="http://localhost:5000",
        data=f"access_token={token}&state=42a85b271b7a652ca3cc4c398cfd3f01b9ad36bf9c945ba823b023e8f8b95c4638576a0e3dcc96838b838bec33ec6c0ee2609d62ed82480b3b8114ca494c0521",
    )
    api_key_auth = requests_auth.HeaderApiKey("my_provided_api_key")
    header = get_header(responses, implicit_auth & api_key_auth)
    assert header.get("Authorization") == f"Bearer {token}"
    assert header.get("X-Api-Key") == "my_provided_api_key"
    tab.assert_success(
        "You are now authenticated on 42a85b271b7a652ca3cc4c398cfd3f01b9ad36bf9c945ba823b023e8f8b95c4638576a0e3dcc96838b838bec33ec6c0ee2609d62ed82480b3b8114ca494c0521. You may close this tab."
    )


def test_oauth2_implicit_and_multiple_authentication_can_be_combined(
    token_cache, responses: RequestsMock, browser_mock: BrowserMock
):
    implicit_auth = requests_auth.OAuth2Implicit("http://provide_token")
    expiry_in_1_hour = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    token = create_token(expiry_in_1_hour)
    tab = browser_mock.add_response(
        opened_url="http://provide_token?response_type=token&state=42a85b271b7a652ca3cc4c398cfd3f01b9ad36bf9c945ba823b023e8f8b95c4638576a0e3dcc96838b838bec33ec6c0ee2609d62ed82480b3b8114ca494c0521&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2F",
        reply_url="http://localhost:5000",
        data=f"access_token={token}&state=42a85b271b7a652ca3cc4c398cfd3f01b9ad36bf9c945ba823b023e8f8b95c4638576a0e3dcc96838b838bec33ec6c0ee2609d62ed82480b3b8114ca494c0521",
    )
    api_key_auth = requests_auth.HeaderApiKey("my_provided_api_key")
    api_key_auth2 = requests_auth.HeaderApiKey(
        "my_provided_api_key2", header_name="X-Api-Key2"
    )
    header = get_header(responses, implicit_auth & (api_key_auth & api_key_auth2))
    assert header.get("Authorization") == f"Bearer {token}"
    assert header.get("X-Api-Key") == "my_provided_api_key"
    assert header.get("X-Api-Key2") == "my_provided_api_key2"
    tab.assert_success(
        "You are now authenticated on 42a85b271b7a652ca3cc4c398cfd3f01b9ad36bf9c945ba823b023e8f8b95c4638576a0e3dcc96838b838bec33ec6c0ee2609d62ed82480b3b8114ca494c0521. You may close this tab."
    )
