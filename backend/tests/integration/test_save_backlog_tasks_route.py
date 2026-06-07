"""
Integration tests for ClickUp backlog task save route.
"""

from fastapi.testclient import TestClient

from backend.src.domain.entities.saved_tasks_request.save_backlog_tasks_request import SaveBacklogTasksRequest
from backend.src.domain.entities.verified_tasks.verified_task_from_backlog import VerifiedTaskFromBacklog


def test_save_backlog_tasks_to_clickup(client: TestClient, container) -> None:
    """
    Test saving verified backlog tasks into ClickUp through the API.
    """
    from backend.src.domain.entities.saved_tasks_request.task_sync_result import TaskSyncResult

    container.save_backlog_task_use_case.save_backlog_tasks_to_clickup.return_value = TaskSyncResult(
        total=1,
        created=1,
        updated=0,
        failed=0,
        failed_tasks=[],
    )

    payload = SaveBacklogTasksRequest(
        tasks=[VerifiedTaskFromBacklog(
            action="create",
            task_name="Build login",
            task_description="Implement login",
            task_assignee="Alice",
            task_status="To Do",
            task_priority="High",
            location="Backend",
            estimation=5,
        )],
        space_id="space-1",
        ignore_names=True,
        ignore_mails=False,
    ).model_dump()

    response = client.post("/clickup/tasks/save-backlog-tasks", json=payload)

    assert response.status_code == 201
    container.save_backlog_task_use_case.save_backlog_tasks_to_clickup.assert_called_once()
    call_args = container.save_backlog_task_use_case.save_backlog_tasks_to_clickup.call_args.kwargs
    assert call_args["space_id"] == "space-1"
    assert call_args["ignore_names"] is True
    assert call_args["ignore_mails"] is False