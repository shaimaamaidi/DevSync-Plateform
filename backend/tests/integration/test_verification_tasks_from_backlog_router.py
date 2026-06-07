"""
Integration tests for backlog task verification routes.
"""

from fastapi.testclient import TestClient

from backend.src.domain.entities.generated_tasks.generated_task_from_backlog import GeneratedTaskFromBacklog
from backend.src.domain.entities.verified_tasks.verified_task_from_backlog import VerifiedTaskFromBacklog


def test_verify_tasks_from_backlog(client: TestClient, container) -> None:
    """
    Test verifying backlog-generated tasks through the API.
    """
    from backend.src.domain.entities.verified_tasks.verified_task_from_summary import VerifiedTaskFromSummary
    from backend.src.domain.entities.generated_tasks.generated_task_from_summary import GeneratedTaskFromSummary

    container.verify_task_use_case.verify_tasks.return_value = [
        VerifiedTaskFromSummary(
            action="create",
            task_name="Build login",
            task_description="Implement login flow",
            task_assignee="Alice",
            task_status="To Do",
            task_priority="High",
            location="Backend",
            task_id=None,
            estimation=5,
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
                estimation=5,
            ).model_dump()
        ],
    }

    response = client.post("/clickup/tasks/verify-from-summary", json=payload)

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["tasks"][0]["action"] == "create"
    container.verify_task_use_case.verify_tasks.assert_called_once()