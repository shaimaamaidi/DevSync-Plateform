"""
Unit tests for ManageClickUpTaskUseCase.
"""

from unittest.mock import MagicMock

import pytest

from backend.src.application.use_cases.manage_clickup_task_use_case import ManageClickUpTaskUseCase
from backend.src.domain.entities.clickup.create_task_request import CreateTaskRequest
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.clickup.update_task_request import UpdateTaskRequest
from backend.src.domain.exceptions.common.invalid_input_exception import InvalidInputException


def test_create_task_resolves_workspace_members_and_calls_writer() -> None:
    """
    Test that creating a task resolves assignee ids and delegates to the writer.
    """
    clickup_writer = MagicMock()
    clickup_reader = MagicMock()
    clickup_reader.get_workspace_members.return_value = [
        {"email": "alice@example.com", "id": "member-1"},
        {"email": "bob@example.com", "id": "member-2"},
    ]
    created_task = ClickUpTask(
        id="task-1",
        name="Build login",
        description="Implement login flow",
        status="to do",
        assignee="alice@example.com",
        priority="high",
    )
    clickup_writer.create_task_by_list.return_value = created_task
    use_case = ManageClickUpTaskUseCase(clickup_writer, clickup_reader)

    request = CreateTaskRequest(
        space_id="space-1",
        list_id="list-1",
        name="Build login",
        description="Implement login flow",
        status="to do",
        priority="high",
        assignees="alice@example.com,bob@example.com",
        ignore_mails=True,
    )

    result = use_case.create_task(request)

    assert result == created_task
    clickup_reader.get_workspace_members.assert_called_once()
    clickup_writer.create_task_by_list.assert_called_once()
    called_list_id, called_task, email_to_id, ignore_mails = clickup_writer.create_task_by_list.call_args.args
    assert called_list_id == "list-1"
    assert called_task.name == "Build login"
    assert email_to_id == {"alice@example.com": "member-1", "bob@example.com": "member-2"}
    assert ignore_mails is True


def test_update_task_resolves_workspace_members_and_calls_writer() -> None:
    """
    Test that updating a task resolves workspace members and delegates to the writer.
    """
    clickup_writer = MagicMock()
    clickup_reader = MagicMock()
    clickup_reader.get_workspace_members.return_value = [
        {"email": "alice@example.com", "id": "member-1"},
    ]
    updated_task = ClickUpTask(
        id="task-1",
        name="Build login v2",
        description="Implement login flow v2",
        status="in progress",
        assignee="alice@example.com",
        priority="high",
    )
    clickup_writer.update_task.return_value = updated_task
    use_case = ManageClickUpTaskUseCase(clickup_writer, clickup_reader)

    request = UpdateTaskRequest(
        space_id="space-1",
        task_id="task-1",
        name="Build login v2",
        description="Implement login flow v2",
        status="in progress",
        priority="high",
        assignees="alice@example.com",
        old_assignees="bob@example.com",
        ignore_mails=False,
    )
    object.__setattr__(request, "list_id", "list-1")

    result = use_case.update_task(request)

    assert result == updated_task
    clickup_reader.get_workspace_members.assert_called_once()
    clickup_writer.update_task.assert_called_once()
    called_task_id, called_task, old_assignees, email_to_id, ignore_mails = clickup_writer.update_task.call_args.args
    assert called_task_id == "task-1"
    assert called_task.name == "Build login v2"
    assert old_assignees == "bob@example.com"
    assert email_to_id == {"alice@example.com": "member-1"}
    assert ignore_mails is False


def test_delete_task_rejects_empty_task_id() -> None:
    """
    Test that deleting a task rejects an empty task id.
    """
    use_case = ManageClickUpTaskUseCase(MagicMock(), MagicMock())

    with pytest.raises(InvalidInputException):
        use_case.delete_task("")


def test_delete_task_calls_writer() -> None:
    """
    Test that deleting a task delegates to the ClickUp writer.
    """
    clickup_writer = MagicMock()
    clickup_writer.delete_task.return_value = True
    use_case = ManageClickUpTaskUseCase(clickup_writer, MagicMock())

    result = use_case.delete_task("task-1")

    assert result is True
    clickup_writer.delete_task.assert_called_once_with("task-1")