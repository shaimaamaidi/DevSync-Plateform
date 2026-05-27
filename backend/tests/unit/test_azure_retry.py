"""
Unit tests for AzureRetry.
"""

from azure.core.exceptions import AzureError, ServiceRequestError

from backend.src.infrastructure.external.backlog_generation.common.azure_retry import AzureRetry


def test_is_retryable_accepts_transient_azure_errors() -> None:
    """
    Test that transient Azure errors are treated as retryable.
    """
    assert AzureRetry.is_retryable(ServiceRequestError("network issue")) is True
    assert AzureRetry.is_retryable(AzureError("HTTP 429 rate limited")) is True
    assert AzureRetry.is_retryable(AzureError("HTTP 503 service unavailable")) is True
    assert AzureRetry.is_retryable(AzureError("timeout while waiting")) is True


def test_is_retryable_rejects_non_transient_errors() -> None:
    """
    Test that non-transient errors are not retried.
    """
    assert AzureRetry.is_retryable(AzureError("authentication failed")) is False
    assert AzureRetry.is_retryable(ValueError("boom")) is False


def test_run_retries_then_succeeds(monkeypatch) -> None:
    """
    Test that run retries transient failures and eventually returns success.
    """
    monkeypatch.setattr("backend.src.infrastructure.external.backlog_generation.common.azure_retry.load_dotenv", lambda *args, **kwargs: True)
    monkeypatch.setenv("WEB_SEARCH_MAX_RETRIES", "3")
    monkeypatch.setenv("WEB_SEARCH_RETRY_BASE_DELAY", "2")
    monkeypatch.setenv("WEB_SEARCH_RETRY_MAX_DELAY", "10")
    monkeypatch.setenv("WEB_SEARCH_RUN_TIMEOUT", "60")

    retry = AzureRetry()
    sleep_calls = []
    monkeypatch.setattr("backend.src.infrastructure.external.backlog_generation.common.azure_retry.random.uniform", lambda a, b: 1.5)

    async def fake_sleep(delay):
        sleep_calls.append(delay)

    monkeypatch.setattr("backend.src.infrastructure.external.backlog_generation.common.azure_retry.asyncio.sleep", fake_sleep)

    attempts = {"count": 0}

    async def flaky_operation():
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise ServiceRequestError("temporary failure")
        return "ok"

    result = __import__("asyncio").run(retry.run(flaky_operation))

    assert result == "ok"
    assert attempts["count"] == 3
    assert sleep_calls == [1.5, 1.5]


def test_run_raises_non_retryable_exception(monkeypatch) -> None:
    """
    Test that run does not retry non-transient failures.
    """
    monkeypatch.setattr("backend.src.infrastructure.external.backlog_generation.common.azure_retry.load_dotenv", lambda *args, **kwargs: True)
    monkeypatch.setenv("WEB_SEARCH_MAX_RETRIES", "3")
    retry = AzureRetry()

    async def bad_operation():
        raise ValueError("bad input")

    try:
        __import__("asyncio").run(retry.run(bad_operation))
        assert False, "expected ValueError"
    except ValueError as exc:
        assert str(exc) == "bad input"