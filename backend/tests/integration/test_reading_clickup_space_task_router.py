"""
Integration tests for ClickUp space task reader routes.
"""

from fastapi.testclient import TestClient

from backend.src.domain.entities.clickup.folder_with_lists import FolderWithLists
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpList, ClickUpTask


def test_get_tasks_by_space(client: TestClient, container) -> None:
    """
    Test retrieving a ClickUp space task tree through the API.
    """
    container.clickup_space_task_reader_use_case.get_tasks_by_space.return_value = [
        FolderWithLists(
            id="folder-1",
            name="Backend",
            lists=[
                ClickUpList(
                    id="list-1",
                    name="Sprint",
                    tasks=[ClickUpTask(id="task-1", name="Build login", description="Implement login", status="done", assignee="alice@example.com", priority="high")],
                    statuses=[],
                    priorities=[],
                )
            ],
        )
    ]

    response = client.get("/clickup/tasks/spaces/space-1")

    assert response.status_code == 200
    assert response.json()[0]["id"] == "folder-1"
    assert response.json()[0]["lists"][0]["tasks"][0]["name"] == "Build login"
    container.clickup_space_task_reader_use_case.get_tasks_by_space.assert_called_once_with("space-1")