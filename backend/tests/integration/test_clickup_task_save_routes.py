"""
Integration tests for ClickUp task save route.
"""

from fastapi.testclient import TestClient

from backend.src.domain.entities.save_tasks.save_tasks_request import SaveTasksRequest
from backend.src.domain.entities.clickup.verified_task import VerifiedTask


def test_save_tasks_to_clickup(client: TestClient, container) -> None:
    """
    Test saving verified tasks into ClickUp through the API.
    """
    container.save_task_use_case.save_to_clickup.return_value = None

    payload = SaveTasksRequest(
        tasks=[VerifiedTask(
            action="create",
            task_name="Build login",
            task_description="Implement login",
            task_assigne="Alice",
            task_status="To Do",
            task_priority="High",
            folder="Backend",
        )],
        space_id="space-1",
        ignore_names=False,
        ignore_mails=True,
    ).model_dump()

    response = client.post("/clickup/save", json=payload)

    assert response.status_code == 201
    assert response.json()["message"] == "Tasks saved to ClickUp successfully."
    assert response.json()["total_tasks"] == 1
    container.save_task_use_case.save_to_clickup.assert_called_once()
    call_args = container.save_task_use_case.save_to_clickup.call_args.kwargs
    assert call_args["space_id"] == "space-1"
    assert call_args["ignore_names"] is False
    assert call_args["ignore_mails"] is True
