"""
Azure retry utility module.

This module provides the AzureRetry class, which implements a resilient
execution strategy for Azure asynchronous operations using:

- Exponential backoff
- Full jitter randomization
- Retry filtering for transient failures only

It is designed to improve the reliability of Azure AI Agent workflows
by automatically handling temporary service disruptions such as:

- Rate limiting (HTTP 429)
- Service unavailability (HTTP 503)
- Transient Azure SDK/network errors
- Short-lived connectivity issues

The retry policy ensures that:
- Business logic errors are NOT retried
- Authentication/configuration errors are NOT retried
- Only transient infrastructure-level failures are retried

Environment variables are used to configure retry behavior with safe defaults,
allowing tuning without code changes.
"""

import asyncio
import logging
import random
from typing import Callable, Awaitable, Any

from azure.core.exceptions import AzureError, ServiceRequestError

from backend.src.infrastructure.config.settings import settings


logger = logging.getLogger(__name__)


class AzureRetry:
    """
    Utility class for retrying Azure async operations using exponential backoff with full jitter.

    This class centralizes retry logic for transient Azure failures such as:
    - throttling (HTTP 429)
    - service unavailability (HTTP 503)
    - temporary network issues
    - transient Azure SDK failures

    It ensures resilient execution of Azure agent operations while avoiding
    retry loops on non-retryable business or configuration errors.

    Configuration is loaded from environment variables with safe defaults:

    Attributes:
            max_attempts (int): Maximum number of retry attempts (default: 3).
            base_delay (float): Initial backoff delay in seconds (default: 2.0).
            max_delay (float): Maximum allowed delay between retries (default: 30.0).
            run_timeout (float): Timeout applied to long-running Azure polling loops (default: 60.0).
    """

    def __init__(self):
        """
        Initialize AzureRetry configuration.

        Loads environment variables and sets retry parameters used for
        exponential backoff execution of Azure operations.
        """
        self.max_attempts = settings.WEB_SEARCH_MAX_RETRIES
        self.base_delay = settings.WEB_SEARCH_RETRY_BASE_DELAY
        self.max_delay = settings.WEB_SEARCH_RETRY_MAX_DELAY
        self.run_timeout = settings.WEB_SEARCH_RUN_TIMEOUT


    @staticmethod
    def is_retryable(exc: Exception) -> bool:
        """
        Determine whether an exception is eligible for retry.

        This method identifies transient failures that can be safely retried,
        such as rate limiting or temporary Azure service issues.

        Args:
            exc (Exception): Exception raised during Azure execution.

        Returns:
            bool: True if the exception is considered retryable, False otherwise.
        """
        if isinstance(exc, ServiceRequestError):
            return True
        if isinstance(exc, AzureError):
            msg = str(exc).lower()
            return any(code in msg for code in ("429", "503", "500", "throttl", "timeout"))
        return False

    async def run(self, coro_factory: Callable[[], Awaitable[Any]]) -> Any:
        """
        Execute a coroutine with retry support using exponential backoff and jitter.

        The coroutine is executed multiple times until success or until
        the maximum number of retry attempts is reached.

        Args:
            coro_factory (Callable[[], Awaitable[Any]]):
                A zero-argument callable returning an awaitable operation.

        Returns:
            Any: The successful result of the coroutine execution.

        Raises:
            Exception: The last encountered exception is raised if:
                - All retry attempts are exhausted, or
                - A non-retryable exception is encountered (e.g. AzureAgentRuntimeException,
                  authentication errors, or unexpected critical failures).
        Notes:
            - Retry is only applied to exceptions considered retryable by `is_retryable`.
            - Backoff strategy uses exponential growth with full jitter.
            - The final raised exception is not wrapped; original exception context is preserved.
        """
        last_exc: Exception | None = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                return await coro_factory()

            except Exception as exc:
                last_exc = exc
                is_last = attempt == self.max_attempts

                if is_last or not self.is_retryable(exc):
                    logger.error(
                        "Attempt %d/%d failed (non-retryable or max reached): %s.",
                        attempt, self.max_attempts, exc,
                    )
                    raise

                raw_delay = self.base_delay * (2 ** (attempt - 1))
                jitter = random.uniform(0, raw_delay)
                delay = min(jitter, self.max_delay)

                logger.warning(
                    "Attempt %d/%d failed — retrying in %.1fs. Error: %s.",
                    attempt, self.max_attempts, delay, exc,
                )
                await asyncio.sleep(delay)

        raise last_exc