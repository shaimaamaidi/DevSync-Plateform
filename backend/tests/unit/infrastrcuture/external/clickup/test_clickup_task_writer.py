"""
Unit tests for ClickUpTaskWriter.

These tests validate create/update/delete flows and the bulk apply logic.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from backend.src.infrastructure.external.clickup.writer.clickup_task_writer import ClickUpTaskWriter
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTaskWithEstimation
from backend.src.domain.exceptions.clickup.clickup_task_create_exception import ClickUpTaskCreateException
from backend.src.domain.exceptions.clickup.clickup_task_delete_exception import ClickUpTaskDeleteException
from backend.src.domain.exceptions.clickup.clickup_task_update_exception import ClickUpTaskUpdateException
from backend.src.infrastructure.external.clickup import writer as clickup_writer_pkg
from backend.src.infrastructure.external.clickup.writer.clickup_task_writer import ClickUpTaskWriter


class DummyResponse:
    def __init__(self, status_code=200, payload=None, text="ok"):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self):
        return self._payload


def test_create_task_by_list_success(monkeypatch) -> None:
    http = SimpleNamespace()
    http.post_raw = lambda endpoint, payload: DummyResponse(status_code=200, payload={"id": "t1"})

    monkeypatch.setattr("backend.src.infrastructure.external.clickup.writer.clickup_task_writer.priority_to_str", lambda p: "low")
    monkeypatch.setattr("backend.src.infrastructure.external.clickup.writer.clickup_task_writer.resolve_assignee_ids_from_mails", lambda e, m, i: [123])
    monkeypatch.setattr("backend.src.infrastructure.external.clickup.writer.clickup_task_writer.parse_task", lambda p: p)

    writer = ClickUpTaskWriter(http)

    task = SimpleNamespace(name="Do things", description="desc", priority=1, status="todo", assignee="alice@example.com")

    result = writer.create_task_by_list("list-1", task, {"alice@example.com": 123}, ignore_mails=True)

    assert result == {"id": "t1"}


def test_create_task_by_list_failure_raises(monkeypatch) -> None:
    http = SimpleNamespace()
    http.post_raw = lambda endpoint, payload: DummyResponse(status_code=500, payload={}, text="err")

    monkeypatch.setattr("backend.src.infrastructure.external.clickup.writer.clickup_task_writer.priority_to_str", lambda p: None)
    monkeypatch.setattr("backend.src.infrastructure.external.clickup.writer.clickup_task_writer.resolve_assignee_ids_from_mails", lambda e, m, i: [])

    writer = ClickUpTaskWriter(http)

    task = SimpleNamespace(name="Fail", description="desc", priority=None, status=None, assignee=None)

    with pytest.raises(ClickUpTaskCreateException):
        writer.create_task_by_list("list-1", task, {}, ignore_mails=True)


def test_update_task_success_and_failure(monkeypatch) -> None:
    http = SimpleNamespace()
    http.put_raw = lambda endpoint, payload: DummyResponse(status_code=200, payload={"id": "u1"})

    monkeypatch.setattr("backend.src.infrastructure.external.clickup.writer.clickup_task_writer.priority_to_str", lambda p: "high")
    monkeypatch.setattr("backend.src.infrastructure.external.clickup.writer.clickup_task_writer.resolve_assignee_ids_from_mails", lambda e, m, i: [5])
    monkeypatch.setattr("backend.src.infrastructure.external.clickup.writer.clickup_task_writer.parse_task", lambda p: p)

    writer = ClickUpTaskWriter(http)

    task_content = SimpleNamespace(name="Update me", description="d", priority=2, status="done", assignee="bob@example.com")

    result = writer.update_task("task-123", task_content, old_assignees="bob@example.com", email_to_id={"bob@example.com": 5}, ignore_mails=True)

    assert result == {"id": "u1"}

    http_fail = SimpleNamespace()
    http_fail.put_raw = lambda endpoint, payload: DummyResponse(status_code=500, payload={}, text="err")
    writer_fail = ClickUpTaskWriter(http_fail)

    with pytest.raises(ClickUpTaskUpdateException):
        writer_fail.update_task("task-123", task_content, old_assignees="bob@example.com", email_to_id={"bob@example.com": 5}, ignore_mails=True)


def test_delete_task_success_and_failure() -> None:
    http = SimpleNamespace()
    http.delete_raw = lambda endpoint: DummyResponse(status_code=204)
    writer = ClickUpTaskWriter(http)

    assert writer.delete_task("task-1") is True

    http_fail = SimpleNamespace()
    http_fail.delete_raw = lambda endpoint: DummyResponse(status_code=500, text="bad")
    writer_fail = ClickUpTaskWriter(http_fail)

    with pytest.raises(ClickUpTaskDeleteException):
        writer_fail.delete_task("task-1")


def test_apply_results_counts() -> None:
    folder = SimpleNamespace(id="fid", name="FolderA", lists=[SimpleNamespace(id="lid", name="List1")])

    create_called = []
    def create_fn(list_id, result, name_to_email, email_to_id, ignore_names, ignore_mails):
        create_called.append((list_id, result.task_name))

    def update_fn(result, name_to_email, email_to_id, ignore_names, ignore_mails):
        pass

    res_create = SimpleNamespace(action="create", location="FolderA / List1", task_name="CreateMe", task_status=None)
    res_update = SimpleNamespace(action="update", task_id=None, task_name="UpdateMe")

    created, updated, skipped = ClickUpTaskWriter._apply_results([res_create, res_update], [folder], [], {}, False, True, create_fn, update_fn)

    assert created == 1
    assert updated == 0
    assert skipped == 1

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
    task = ClickUpTaskWithEstimation(
        id=None,
        name="Task 1",
        description="Do work",
        status="open",
        assignee="alice@example.com, bob@example.com",
        priority="high",
        estimation=None
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
            ClickUpTaskWithEstimation(id=None, name="Task 1", description=None, status=None, assignee=None, priority=None, estimation=None),
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
    task = ClickUpTaskWithEstimation(
        id="task-1",
        name="Task 1",
        description="Do work",
        status="open",
        assignee="alice@example.com",
        priority=None,
        estimation=None
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
