"""
Integration tests for ClickUp task generation and verification routes.
"""

from fastapi.testclient import TestClient

from backend.src.domain.entities.generate_tasks_from_summary.generated_task import GeneratedTask
from backend.src.domain.entities.verify_tasks.verified_task import VerifiedTask
from backend.src.domain.entities.generate_tasks_from_summary.generate_tasks_request import GenerateTasksFromSummaryRequest
from backend.src.domain.entities.verify_tasks.verify_tasks_request import VerifyTasksRequest


def test_generate_tasks_from_summary(client: TestClient, container) -> None:
    """
    Test generating tasks from a meeting summary through the API.
    """
    generated_task = {
        "task_name": "Build login",
        "task_description": "Implement login flow",
        "task_assigne": "Alice",
        "task_status": "To Do",
        "task_priority": "High",
        "folder": "Backend",
    }

    container.generate_task_from_summary_use_case.generate_tasks_from_meeting_summary.return_value = [
        generated_task,
    ]

    payload = GenerateTasksFromSummaryRequest(
        meeting_summary="Discussed login and onboarding",
        space_id="space-1",
    ).model_dump()

    response = client.post("/clickup/generate-tasks-from-summary", json=payload)

    assert response.status_code == 200
    assert response.json()[0]["task_name"] == "Build login"
    container.generate_task_from_summary_use_case.generate_tasks_from_meeting_summary.assert_called_once_with(
        meeting_summary="Discussed login and onboarding",
        space_id="space-1",
    )


def test_verify_tasks(client: TestClient, container) -> None:
    """
    Test verifying generated tasks through the API.
    """
    generated_task = GeneratedTask(
        task_name="Build login",
        task_description="Implement login flow",
        task_assigne="Alice",
        task_status="To Do",
        task_priority="High",
        folder="Backend",
    )

    verified_task = VerifiedTask(
        action="create",
        task_name="Build login",
        task_description="Implement login flow",
        task_assigne="Alice",
        task_status="To Do",
        task_priority="High",
        folder="Backend",
        task_id=None,
    )

    container.verify_task_use_case.verify_tasks.return_value = [verified_task]

    payload = VerifyTasksRequest(
        space_id="space-1",
        tasks=[generated_task],
    ).model_dump()

    response = client.post("/clickup/verify", json=payload)

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["tasks"][0]["action"] == "create"
    container.verify_task_use_case.verify_tasks.assert_called_once_with(
        tasks=[generated_task],
        space_id="space-1",
    )
