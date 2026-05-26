"""
Integration tests for ClickUp task generation and verification routes.
"""

from fastapi.testclient import TestClient

from backend.src.domain.entities.generated_tasks.generated_task_from_summary import GeneratedTaskFromSummary
from backend.src.domain.entities.verified_tasks.verified_task_from_summary import VerifiedTaskFromSummary
from backend.src.domain.entities.generated_tasks.generated_task_from_summary_request import GeneratedTaskFromSummaryRequest
from backend.src.domain.entities.verified_tasks.verified_task_from_summary_request import VerifiedTaskFromSummaryRequest


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
        "location": "Backend",
    }

    container.generate_task_from_summary_use_case.generate_tasks_from_meeting_summary.return_value = [
        generated_task,
    ]

    payload = GeneratedTaskFromSummaryRequest(
        meeting_summary="Discussed login and onboarding",
        space_id="space-1",
    ).model_dump()

    response = client.post("/clickup/tasks/generate-tasks-from-summary", json=payload)

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
    generated_task = GeneratedTaskFromSummary(
        task_name="Build login",
        task_description="Implement login flow",
        task_assigne="Alice",
        task_status="To Do",
        task_priority="High",
        location="Backend",
    )

    verified_task = VerifiedTaskFromSummary(
        action="create",
        task_name="Build login",
        task_description="Implement login flow",
        task_assigne="Alice",
        task_status="To Do",
        task_priority="High",
        location="Backend",
        task_id=None,
    )

    container.verify_task_use_case.verify_tasks.return_value = [verified_task]

    payload = VerifiedTaskFromSummaryRequest(
        space_id="space-1",
        tasks=[generated_task],
    ).model_dump()

    response = client.post("/clickup/tasks/verify-from-summary", json=payload)

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["tasks"][0]["action"] == "create"
    container.verify_task_use_case.verify_tasks.assert_called_once_with(
        tasks=[generated_task],
        space_id="space-1",
    )
