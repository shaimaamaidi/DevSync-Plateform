"""
Unit tests for GenerateBacklogUseCase.
"""

import pytest
from unittest.mock import MagicMock

from backend.src.application.use_cases.generate_backlog_use_case import GenerateBacklogUseCase
from backend.src.domain.entities.backlog.reply_backlog_stream_request import ReplyBacklogStreamRequest
from backend.src.domain.entities.backlog.reply_stream_request import ReplyStreamRequest
from backend.src.domain.entities.backlog.start_backlog_request import StartBacklogRequest
from backend.src.domain.exceptions.base.app_exception import AppException
from backend.src.domain.exceptions.backlog.backlog_reply_exception import BacklogReplyException
from backend.src.domain.exceptions.backlog.backlog_stream_exception import BacklogStreamException
from backend.src.domain.exceptions.stream.reply_stream_exception import ReplyStreamException


def _async_stream(chunks: list[str]):
    async def _gen():
        for chunk in chunks:
            yield chunk

    return _gen()


def _async_raise(exc: Exception):
    async def _gen():
        raise exc
    yield  # pragma: no cover

    return _gen()

@pytest.mark.asyncio
async def test_start_stream_success() -> None:
    """
    Start returns streamed chunks from orchestrator.
    """
    orchestrator = MagicMock()
    orchestrator.start_stream.return_value = _async_stream(["a", "b"])

    use_case = GenerateBacklogUseCase(orchestrator)
    request = StartBacklogRequest(description="Build a CRM")

    result = []
    async for chunk in use_case.start(request):
        result.append(chunk)

    assert result == ["a", "b"]
    orchestrator.start_stream.assert_called_once_with("Build a CRM")


@pytest.mark.asyncio
async def test_start_stream_app_exception_passthrough() -> None:
    """
    Start re-raises AppException from orchestrator.
    """
    orchestrator = MagicMock()
    orchestrator.start_stream.return_value = _async_raise(AppException("boom"))

    use_case = GenerateBacklogUseCase(orchestrator)
    request = StartBacklogRequest(description="desc")

    with pytest.raises(AppException):
        async for _ in use_case.start(request):
            pass


@pytest.mark.asyncio
async def test_start_stream_wraps_unexpected_exception() -> None:
    """
    Start wraps unexpected exceptions into BacklogStreamException.
    """
    orchestrator = MagicMock()
    orchestrator.start_stream.return_value = _async_raise(RuntimeError("fail"))

    use_case = GenerateBacklogUseCase(orchestrator)
    request = StartBacklogRequest(description="desc")

    with pytest.raises(BacklogStreamException):
        async for _ in use_case.start(request):
            pass


@pytest.mark.asyncio
async def test_reply_stream_success() -> None:
    """
    Reply returns streamed chunks from orchestrator.
    """
    orchestrator = MagicMock()
    orchestrator.reply_stream.return_value = _async_stream(["ok"])

    use_case = GenerateBacklogUseCase(orchestrator)
    request = ReplyStreamRequest(thread_id="t1", tool_result="{}", user_result="{}")

    result = []
    async for chunk in use_case.reply(request):
        result.append(chunk)

    assert result == ["ok"]
    orchestrator.reply_stream.assert_called_once_with(
        thread_id="t1",
        tool_result="{}",
        user_result="{}",
    )


@pytest.mark.asyncio
async def test_reply_stream_wraps_unexpected_exception() -> None:
    """
    Reply wraps unexpected exceptions into ReplyStreamException.
    """
    orchestrator = MagicMock()
    orchestrator.reply_stream.return_value = _async_raise(ValueError("bad"))

    use_case = GenerateBacklogUseCase(orchestrator)
    request = ReplyStreamRequest(thread_id="t1", tool_result="{}", user_result="{}")

    with pytest.raises(ReplyStreamException):
        async for _ in use_case.reply(request):
            pass


@pytest.mark.asyncio
async def test_reply_backlog_stream_success() -> None:
    """
    Reply backlog returns streamed chunks from orchestrator.
    """
    orchestrator = MagicMock()
    orchestrator.reply_backlog_stream.return_value = _async_stream(["fixed"])

    use_case = GenerateBacklogUseCase(orchestrator)
    request = ReplyBacklogStreamRequest(
        thread_id="t2",
        tool_result="{\"backlog\": []}",
        user_result="{\"backlog\": []}",
    )

    result = []
    async for chunk in use_case.reply_backlog(request):
        result.append(chunk)

    assert result == ["fixed"]
    orchestrator.reply_backlog_stream.assert_called_once_with(
        thread_id="t2",
        user_result="{\"backlog\": []}",
        tool_result="{\"backlog\": []}",
    )


@pytest.mark.asyncio
async def test_reply_backlog_stream_wraps_unexpected_exception() -> None:
    """
    Reply backlog wraps unexpected exceptions into BacklogReplyException.
    """
    orchestrator = MagicMock()
    orchestrator.reply_backlog_stream.return_value = _async_raise(KeyError("oops"))

    use_case = GenerateBacklogUseCase(orchestrator)
    request = ReplyBacklogStreamRequest(
        thread_id="t2",
        tool_result="{\"backlog\": []}",
        user_result="{\"backlog\": []}",
    )

    with pytest.raises(BacklogReplyException):
        async for _ in use_case.reply_backlog(request):
            pass
