"""
Unit tests for ClickUpHttpClient.
"""

from types import SimpleNamespace

import pytest

from backend.src.domain.exceptions.clickup.clickup_api_exception import ClickUpApiException
from backend.src.domain.exceptions.clickup.clickup_authentication_exception import ClickUpAuthenticationException
from backend.src.domain.exceptions.clickup.clickup_client_exception import ClickUpClientException
from backend.src.domain.exceptions.clickup.clickup_rate_limit_exception import ClickUpRateLimitException
from backend.src.domain.exceptions.clickup.clickup_resource_not_found_exception import ClickUpResourceNotFoundException
from backend.src.domain.exceptions.clickup.missing_clickup_config_exception import MissingClickUpConfigException
from backend.src.infrastructure.external.clickup.client.clickup_http_client import ClickUpHttpClient


def test_clickup_http_client_initializes_headers(monkeypatch) -> None:
    """
    Test that the ClickUp HTTP client reads the environment and prepares headers.
    """
    monkeypatch.setattr("backend.src.infrastructure.external.clickup.client.clickup_http_client.load_dotenv", lambda *args, **kwargs: True)
    monkeypatch.setenv("CLICKUP_API_TOKEN", "token-123")
    monkeypatch.setenv("CLICKUP_TEAM_ID", "team-456")

    client = ClickUpHttpClient()

    assert client.team_id == "team-456"
    assert client._headers == {
        "Authorization": "token-123",
        "Content-Type": "application/json",
    }


def test_clickup_http_client_raises_when_configuration_is_missing(monkeypatch) -> None:
    """
    Test that the ClickUp HTTP client raises when required configuration is missing.
    """
    monkeypatch.setattr("backend.src.infrastructure.external.clickup.client.clickup_http_client.load_dotenv", lambda *args, **kwargs: True)
    monkeypatch.delenv("CLICKUP_API_TOKEN", raising=False)
    monkeypatch.delenv("CLICKUP_TEAM_ID", raising=False)

    try:
        ClickUpHttpClient()
    except MissingClickUpConfigException:
        assert True
    else:
        raise AssertionError("Expected MissingClickUpConfigException")


@pytest.mark.parametrize(
    "status_code, expected_exception, headers",
    [
        (401, ClickUpAuthenticationException, {}),
        (404, ClickUpResourceNotFoundException, {}),
        (429, ClickUpRateLimitException, {"Retry-After": "12"}),
        (400, ClickUpClientException, {}),
        (500, ClickUpApiException, {}),
    ],
)
def test_clickup_http_client_handles_response_status_codes(status_code, expected_exception, headers) -> None:
    """
    Test that ClickUp HTTP errors are mapped to the expected domain exceptions.
    """
    response = SimpleNamespace(status_code=status_code, headers=headers)

    with pytest.raises(expected_exception):
        ClickUpHttpClient._handle_response(response)