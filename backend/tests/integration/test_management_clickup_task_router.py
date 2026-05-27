"""
Integration tests for ClickUp task management routes.
"""

from fastapi.testclient import TestClient

from backend.src.domain.entities.clickup.create_task_request import CreateTaskRequest
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.clickup.update_task_request import UpdateTaskRequest


def test_create_clickup_task(client: TestClient, container) -> None:
    """
    Test creating a ClickUp task through the API.
    """
    container.clickup_task_creation_use_case.create_task.return_value = ClickUpTask(
        id="task-1",
        name="Build login",
        description="Implement login flow",
        status="to do",
        assignee="alice@example.com",
        priority="high",
    )

    payload = CreateTaskRequest(
        space_id="space-1",
        list_id="list-1",
        name="Build login",
        description="Implement login flow",
        status="to do",
        priority="high",
        assignees="alice@example.com",
        ignore_mails=True,
    ).model_dump()

    response = client.post("/clickup/tasks/manage/", json=payload)

    assert response.status_code == 201
    assert response.json()["id"] == "task-1"
    container.clickup_task_creation_use_case.create_task.assert_called_once()


def test_update_clickup_task(client: TestClient, container) -> None:
    """
    Test updating a ClickUp task through the API.
    """
    container.clickup_task_creation_use_case.update_task.return_value = ClickUpTask(
        id="task-1",
        name="Build login v2",
        description="Implement login flow v2",
        status="in progress",
        assignee="alice@example.com",
        priority="high",
    )

    payload = UpdateTaskRequest(
        space_id="space-1",
        task_id="task-1",
        name="Build login v2",
        description="Implement login flow v2",
        status="in progress",
        priority="high",
        assignees="alice@example.com",
        old_assignees="bob@example.com",
        ignore_mails=False,
    ).model_dump()

    response = client.put("/clickup/tasks/manage/space-1", json=payload)

    assert response.status_code == 200
    assert response.json()["id"] == "task-1"
    container.clickup_task_creation_use_case.update_task.assert_called_once()


def test_delete_clickup_task(client: TestClient, container) -> None:
    """
    Test deleting a ClickUp task through the API.
    """
    container.clickup_task_creation_use_case.delete_task.return_value = True

    response = client.delete("/clickup/tasks/manage/task-1")

    assert response.status_code == 200
    assert response.json() is True
    container.clickup_task_creation_use_case.delete_task.assert_called_once_with("task-1")