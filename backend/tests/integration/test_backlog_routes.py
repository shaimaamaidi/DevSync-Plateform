"""
Integration tests for backlog generation routes.
"""

from fastapi.testclient import TestClient


def _event_stream(chunks: list[str]):
    async def _stream():
        for chunk in chunks:
            yield chunk

    return _stream()


def test_start_backlog_stream(client: TestClient, container) -> None:
    """
    Test starting backlog generation returns a streaming response.
    """
    container.backlog_use_case.start.return_value = _event_stream([
        "data: {\"thread_id\": \"t-123\"}\n\n",
        "data: {\"text\": \"chunk\"}\n\n",
    ])

    response = client.post("/backlog/start", json={"description": "Build a CRM"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    container.backlog_use_case.start.assert_called_once()
    request = container.backlog_use_case.start.call_args[0][0]
    assert request.description == "Build a CRM"


def test_reply_backlog_stream(client: TestClient, container) -> None:
    """
    Test replying to market intelligence verification returns a streaming response.
    """
    container.backlog_use_case.reply.return_value = _event_stream([
        "data: {\"text\": \"reply\"}\n\n",
    ])

    payload = {
        "thread_id": "t-456",
        "tool_result": "{\"k\": 1}",
        "user_result": "{\"k\": 1}",
    }
    response = client.post("/backlog/reply", json=payload)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    container.backlog_use_case.reply.assert_called_once()
    request = container.backlog_use_case.reply.call_args[0][0]
    assert request.thread_id == "t-456"
    assert request.tool_result == "{\"k\": 1}"
    assert request.user_result == "{\"k\": 1}"


def test_reply_backlog_validation_stream(client: TestClient, container) -> None:
    """
    Test replying to backlog validation returns a streaming response.
    """
    container.backlog_use_case.reply_backlog.return_value = _event_stream([
        "data: {\"text\": \"fixed\"}\n\n",
    ])

    payload = {
        "thread_id": "t-789",
        "tool_result": "{\"backlog\": []}",
        "user_result": "{\"backlog\": []}",
    }
    response = client.post("/backlog/reply/backlog", json=payload)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    container.backlog_use_case.reply_backlog.assert_called_once()
    request = container.backlog_use_case.reply_backlog.call_args[0][0]
    assert request.thread_id == "t-789"
    assert request.tool_result == "{\"backlog\": []}"
    assert request.user_result == "{\"backlog\": []}"
