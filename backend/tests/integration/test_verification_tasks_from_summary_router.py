"""
Integration tests for summary task verification routes.
"""

from fastapi.testclient import TestClient

from backend.src.domain.entities.generated_tasks.generated_task_from_summary import GeneratedTaskFromSummary
from backend.src.domain.entities.verified_tasks.verified_task_from_summary import VerifiedTaskFromSummary


def test_verify_tasks_from_summary(client: TestClient, container) -> None:
    """
    Test verifying summary-generated tasks through the API.
    """
    container.verify_task_use_case.verify_tasks.return_value = [
        VerifiedTaskFromSummary(
            action="update",
            task_name="Build login",
            task_description="Implement login flow",
            task_assignee="Alice",
            task_status="To Do",
            task_priority="High",
            location="Backend",
            task_id="task-1",
        )
    ]

    payload = {
        "space_id": "space-1",
        "tasks": [
            GeneratedTaskFromSummary(
                task_name="Build login",
                task_description="Implement login flow",
                task_assignee="Alice",
                task_status="To Do",
                task_priority="High",
                location="Backend",
            ).model_dump()
        ],
    }

    response = client.post("/clickup/tasks/verify-from-summary", json=payload)

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["tasks"][0]["action"] == "update"
    container.verify_task_use_case.verify_tasks.assert_called_once()