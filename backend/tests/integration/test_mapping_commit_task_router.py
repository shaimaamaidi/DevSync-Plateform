"""
Integration tests for commit-to-task mapping routes.
"""

from fastapi.testclient import TestClient

from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.mapped_commit_task.mapped_commit_task_reponse import CommitTaskMappingStatus, MappedCommitTaskResponse


def test_find_task_by_commit(client: TestClient, container) -> None:
    """
    Test mapping a commit to a ClickUp task through the API.
    """
    container.commit_task_mapping_use_case.map_commit_task.return_value = MappedCommitTaskResponse(
        status=CommitTaskMappingStatus.FOUND,
        message="Task found.",
        task=ClickUpTask(
            id="task-1",
            name="Build login",
            description="Implement login flow",
            status="done",
            assignee="alice@example.com",
            priority="high",
        ),
    )

    response = client.post(
        "/commit-traceability/find-task-by-commit",
        json={"commit": "fix login flow", "space_id": "space-1"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "FOUND"
    assert response.json()["task"]["id"] == "task-1"
    container.commit_task_mapping_use_case.map_commit_task.assert_called_once_with(
        commit="fix login flow",
        space_id="space-1",
    )