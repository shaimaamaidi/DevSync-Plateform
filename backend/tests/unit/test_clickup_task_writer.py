"""
Unit tests for ClickUpTaskWriter.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.verified_tasks.verified_task_from_summary import VerifiedTaskFromSummary
from backend.src.domain.exceptions.clickup.clickup_task_create_exception import ClickUpTaskCreateException
from backend.src.domain.exceptions.clickup.clickup_task_delete_exception import ClickUpTaskDeleteException
from backend.src.domain.exceptions.clickup.clickup_task_update_exception import ClickUpTaskUpdateException
from backend.src.infrastructure.external.clickup import writer as clickup_writer_pkg
from backend.src.infrastructure.external.clickup.writer.clickup_task_writer import ClickUpTaskWriter


def test_create_task_by_list_builds_payload_and_returns_parsed_task(monkeypatch) -> None:
    """
    Test that task creation builds the expected payload and parses the response.
    """
    http_client = MagicMock()
    response = SimpleNamespace(status_code=200, json=lambda: {"id": "task-1", "name": "Task 1"})
    http_client.post_raw.return_value = response

    monkeypatch.setattr(clickup_writer_pkg.clickup_task_writer, "priority_to_str", lambda value: "high")
    monkeypatch.setattr(clickup_writer_pkg.clickup_task_writer, "resolve_assignee_ids_from_mails", lambda *args: [11, 22])
    monkeypatch.setattr(clickup_writer_pkg.clickup_task_writer, "parse_task", lambda payload: payload)

    writer = ClickUpTaskWriter(http_client)
    task = ClickUpTask(
        id=None,
        name="Task 1",
        description="Do work",
        status="open",
        assignee="alice@example.com, bob@example.com",
        priority="high",
    )

    result = writer.create_task_by_list("list-1", task, {"alice@example.com": 11, "bob@example.com": 22}, False)

    http_client.post_raw.assert_called_once_with(
        "/list/list-1/task",
        {
            "name": "Task 1",
            "description": "Do work",
            "priority": "high",
            "status": "open",
            "assignees": [11, 22],
        },
    )
    assert result == {"id": "task-1", "name": "Task 1"}


def test_create_task_by_list_raises_when_api_fails(monkeypatch) -> None:
    """
    Test that task creation raises when ClickUp does not return success.
    """
    http_client = MagicMock()
    http_client.post_raw.return_value = SimpleNamespace(status_code=400, text="bad", json=lambda: {})
    monkeypatch.setattr(clickup_writer_pkg.clickup_task_writer, "priority_to_str", lambda value: None)
    monkeypatch.setattr(clickup_writer_pkg.clickup_task_writer, "resolve_assignee_ids_from_mails", lambda *args: [])

    writer = ClickUpTaskWriter(http_client)

    with pytest.raises(ClickUpTaskCreateException):
        writer.create_task_by_list(
            "list-1",
            ClickUpTask(id=None, name="Task 1", description=None, status=None, assignee=None, priority=None),
            {},
            False,
        )


def test_update_task_builds_assignee_delta(monkeypatch) -> None:
    """
    Test that task update computes assignee additions and removals.
    """
    http_client = MagicMock()
    http_client.put_raw.return_value = SimpleNamespace(status_code=200, json=lambda: {"id": "task-1", "name": "Task 1"})
    monkeypatch.setattr(clickup_writer_pkg.clickup_task_writer, "priority_to_str", lambda value: None)
    monkeypatch.setattr(clickup_writer_pkg.clickup_task_writer, "resolve_assignee_ids_from_mails", lambda email_to_id, mails, ignore_mails: [email_to_id[mails[0]]])
    monkeypatch.setattr(clickup_writer_pkg.clickup_task_writer, "parse_task", lambda payload: payload)

    writer = ClickUpTaskWriter(http_client)
    task = ClickUpTask(
        id="task-1",
        name="Task 1",
        description="Do work",
        status="open",
        assignee="alice@example.com",
        priority=None,
    )

    result = writer.update_task("task-1", task, "bob@example.com", {"alice@example.com": 11, "bob@example.com": 22}, False)

    http_client.put_raw.assert_called_once()
    payload = http_client.put_raw.call_args.args[1]
    assert payload["assignees"] == {"add": [11], "rem": [22]}
    assert result == {"id": "task-1", "name": "Task 1"}


def test_delete_task_returns_true_on_success() -> None:
    """
    Test that task deletion returns True when ClickUp accepts the delete request.
    """
    http_client = MagicMock()
    http_client.delete_raw.return_value = SimpleNamespace(status_code=204, text="")

    writer = ClickUpTaskWriter(http_client)

    assert writer.delete_task("task-1") is True
    http_client.delete_raw.assert_called_once_with("/task/task-1")


def test_delete_task_raises_on_failure() -> None:
    """
    Test that task deletion raises when ClickUp rejects the delete request.
    """
    http_client = MagicMock()
    http_client.delete_raw.return_value = SimpleNamespace(status_code=500, text="fail")

    writer = ClickUpTaskWriter(http_client)

    with pytest.raises(ClickUpTaskDeleteException):
        writer.delete_task("task-1")
