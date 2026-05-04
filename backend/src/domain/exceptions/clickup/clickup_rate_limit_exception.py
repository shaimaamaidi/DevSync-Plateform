"""
ClickUp rate limit exception.

This module defines the ClickUpRateLimitException, a specialized exception used
to handle cases where the ClickUp API rate limit is exceeded (HTTP 429).
It provides structured information to support retry strategies with backoff.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class ClickUpRateLimitException(AppException):
    """
    Exception for ClickUp API rate limit errors.

    This exception is raised when the ClickUp API returns HTTP 429 due to
    too many requests in a short period of time. It indicates that the request
    may be retried after a delay.

    Attributes:
        message: Human-readable error message.
        code: Stable internal error code identifying the error type.
        http_status: HTTP status code associated with the error.
        retry_after: Optional delay (in seconds) before retrying the request.
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded.",
        retry_after: int | None = None
    ):
        """
        Initialize a ClickUp rate limit exception.

        Args:
            message (str): Human-readable error message.
            retry_after (int | None): Suggested wait time before retrying (if provided by API).
        """
        super().__init__(
            message=message,
            code="CLICKUP_RATE_LIMIT",
            http_status=429
        )
        self.retry_after = retry_after