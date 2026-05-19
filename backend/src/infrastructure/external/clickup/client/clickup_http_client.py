"""
HTTP client for ClickUp API interactions.

This module defines the ClickUpHttpClient class, which provides a low-level
transport layer for interacting with the ClickUp v2 REST API. It is responsible
for executing HTTP requests (GET, POST, PUT) and translating HTTP errors into
domain-specific exceptions.

This client contains no business logic and is used by infrastructure services.
"""

import logging
import os
from pathlib import Path

import requests
from typing import Any

from dotenv import load_dotenv

from backend.src.domain.exceptions.clickup.clickup_api_exception import ClickUpApiException
from backend.src.domain.exceptions.clickup.clickup_authentication_exception import ClickUpAuthenticationException
from backend.src.domain.exceptions.clickup.clickup_client_exception import ClickUpClientException
from backend.src.domain.exceptions.clickup.clickup_rate_limit_exception import ClickUpRateLimitException
from backend.src.domain.exceptions.clickup.clickup_resource_not_found_exception import ClickUpResourceNotFoundException
from backend.src.domain.exceptions.clickup.missing_clickup_config_exception import MissingClickUpConfigException


logger = logging.getLogger(__name__)


_BACKEND_DIR = Path(__file__).resolve().parents[5]
_DOTENV_PATH = _BACKEND_DIR / ".env"


class ClickUpHttpClient:
    """
    Base HTTP client for ClickUp API communication.

    This class centralizes:
    - Authentication via environment variables
    - HTTP request execution (GET, POST, PUT)
    - Error handling and mapping to domain exceptions

    Attributes:
        BASE_URL (str): Base URL for ClickUp API.
        _headers (dict): HTTP headers including authentication token.
    """

    BASE_URL = "https://api.clickup.com/api/v2"

    def __init__(self):
        """
        Initialize the ClickUp HTTP client.

        Loads environment variables, validates the presence of the ClickUp API token,
        and prepares HTTP headers for authenticated requests.

        Raises:
            MissingClickUpConfigException: If the API token is missing from environment.
        """
        loaded = load_dotenv(_DOTENV_PATH, override=False)

        if not loaded:
            logger.warning(".env file not found at %s.", _DOTENV_PATH)

        api_token = os.getenv("CLICKUP_API_TOKEN")
        self.team_id = os.getenv("CLICKUP_TEAM_ID")

        if not api_token or not self.team_id:
            raise MissingClickUpConfigException(
                "ClickUp integration is not properly configured. Please contact your administrator."
            )

        self._headers = {
            "Authorization": api_token,
            "Content-Type": "application/json",
        }


    def get(self, endpoint: str) -> Any:
        """
        Send a GET request to ClickUp API.

        Args:
            endpoint: API endpoint path starting with '/'.

        Returns:
            Parsed JSON response.

        Raises:
            ClickUpAuthenticationException: If authentication or authorization fails (401, 403).
            ClickUpResourceNotFoundException: If resource is not found (404).
            ClickUpRateLimitException: If rate limit is exceeded (429).
            ClickUpClientException: For client-side errors (400–499 excluding handled cases).
            ClickUpApiException: For server errors (5xx or network-related errors).
        """
        logger.info("GET %s", endpoint)

        try:
            response = requests.get(f"{self.BASE_URL}{endpoint}", headers=self._headers)
            self._handle_response(response)
            return response.json()

        except (ClickUpAuthenticationException, ClickUpResourceNotFoundException, ClickUpClientException,
                ClickUpRateLimitException, ClickUpApiException):
            logger.error("API error on GET %s.", endpoint, exc_info=True)
            raise
        except (requests.exceptions.RequestException, ValueError) as e:
            logger.error("Network error on GET %s.", endpoint, exc_info=True)
            raise ClickUpApiException(
                "Unable to reach ClickUp. Please check your internet connection and try again."
            ) from e

    def post(self, endpoint: str, payload: dict) -> Any:
        """
        Send a POST request to ClickUp API.

        Args:
            endpoint: API endpoint path starting with '/'.
            payload: JSON payload to send.

        Returns:
            Parsed JSON response.

        Raises:
            ClickUpAuthenticationException: If authentication or authorization fails (401, 403).
            ClickUpResourceNotFoundException: If resource is not found (404).
            ClickUpRateLimitException: If rate limit is exceeded (429).
            ClickUpClientException: For client-side errors (400–499 excluding handled cases).
            ClickUpApiException: For server errors (5xx or network-related errors).
        """
        logger.info("POST %s", endpoint)

        try:
            response = requests.post(
                f"{self.BASE_URL}{endpoint}",
                json=payload,
                headers=self._headers
            )
            self._handle_response(response)
            return response.json()

        except (ClickUpAuthenticationException, ClickUpResourceNotFoundException, ClickUpClientException,
                ClickUpRateLimitException, ClickUpApiException):
            logger.error("API error on POST %s.", endpoint, exc_info=True)
            raise
        except (requests.exceptions.RequestException, ValueError) as e:
            logger.error("Network error on POST %s.", endpoint, exc_info=True)
            raise ClickUpApiException(
                "Unable to reach ClickUp. Please check your internet connection and try again."
            ) from e

    def post_raw(self, endpoint: str, payload: dict) -> requests.Response:
        """
        Send a POST request and return the raw HTTP response.

        Args:
            endpoint: API endpoint path starting with '/'.
            payload: JSON payload to send.

        Returns:
            Raw HTTP response object.
        """
        logger.info("POST (raw) %s", endpoint)

        return requests.post(
            f"{self.BASE_URL}{endpoint}",
            json=payload,
            headers=self._headers
        )

    def put(self, endpoint: str, payload: dict) -> Any:
        """
        Send a PUT request to ClickUp API.

        Args:
            endpoint: API endpoint path starting with '/'.
            payload: JSON payload to send.

        Returns:
            Parsed JSON response.

        Raises:
            ClickUpAuthenticationException: If authentication or authorization fails (401, 403).
            ClickUpResourceNotFoundException: If resource is not found (404).
            ClickUpRateLimitException: If rate limit is exceeded (429).
            ClickUpClientException: For client-side errors (400–499 excluding handled cases).
            ClickUpApiException: For server errors (5xx or network-related errors).
        """
        logger.info("PUT %s", endpoint)

        try:
            response = requests.put(
                f"{self.BASE_URL}{endpoint}",
                json=payload,
                headers=self._headers
            )
            self._handle_response(response)
            return response.json()

        except (ClickUpAuthenticationException, ClickUpResourceNotFoundException,ClickUpClientException,
                ClickUpRateLimitException, ClickUpApiException):
            logger.error("API error on PUT %s.", endpoint, exc_info=True)
            raise
        except (requests.exceptions.RequestException, ValueError) as e:
            logger.error("Network error on PUT %s.", endpoint, exc_info=True)
            raise ClickUpApiException(
                "Unable to reach ClickUp. Please check your internet connection and try again."
            ) from e

    def put_raw(self, endpoint: str, payload: dict) -> requests.Response:
        """
        Send a PUT request and return the raw HTTP response.

        Args:
            endpoint: API endpoint path starting with '/'.
            payload: JSON payload to send.

        Returns:
            Raw HTTP response object.
        """
        logger.info("PUT (raw) %s", endpoint)

        return requests.put(
            f"{self.BASE_URL}{endpoint}",
            json=payload,
            headers=self._headers
        )

    def delete_raw(self, endpoint: str) -> requests.Response:
        logger.info("DELETE (raw) %s", endpoint)

        return requests.delete(
            f"{self.BASE_URL}{endpoint}",
            headers=self._headers
        )

    @staticmethod
    def _handle_response(response: requests.Response) -> None:
        """
        Handle HTTP responses and map errors to domain exceptions.

        Args:
            response: HTTP response returned by ClickUp API.

        Raises:
            ClickUpAuthenticationException: If status code is 401 or 403.
            ClickUpResourceNotFoundException: If status code is 404.
            ClickUpRateLimitException: If status code is 429.
            ClickUpClientException: For other client errors (4xx).
            ClickUpApiException: For server errors (5xx).
        """
        status = response.status_code

        if status in (401, 403):
            raise ClickUpAuthenticationException(
                "ClickUp integration is not properly configured. Please contact your administrator."
            )

        if status == 404:
            raise ClickUpResourceNotFoundException(
                "The requested ClickUp resource could not be found. It may have been deleted or moved."
            )

        if status == 429:
            retry_after = response.headers.get("Retry-After")
            raise ClickUpRateLimitException(
                message="Too many requests sent to ClickUp. Please wait a moment before trying again.",
                retry_after=int(retry_after) if retry_after else None
            )

        if 400 <= status < 500:
            raise ClickUpClientException(
                "The request to ClickUp was invalid. Please verify your input and try again."
            )

        if status >= 500:
            raise ClickUpApiException(
                "ClickUp is currently experiencing issues. Please try again later."
            )

