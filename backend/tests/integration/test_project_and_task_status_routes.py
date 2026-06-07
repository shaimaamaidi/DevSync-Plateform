"""
Integration tests for project and task status routes.
"""

from datetime import datetime
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from backend.src.domain.entities.checked_project_status.project_status_summary import ProjectStatusCode, ProjectStatusSummary, TaskSummary
from backend.src.domain.entities.checked_task_status.synthesized_task_status_result import SynthesizedTaskStatusResult
from backend.src.domain.entities.checked_task_status.task_search_response import TaskSearchResponse, TaskSearchStatus
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.github.commit import CommitDTO
from backend.src.domain.entities.github.deployment import DeploymentDTO
from backend.src.domain.entities.mapped_commit_task.mapped_commit_task_reponse import CommitTaskMappingStatus, MappedCommitTaskResponse
from backend.src.domain.entities.shared.project_space_request import ProjectSpaceRequest
from backend.src.domain.entities.weekly_project_summary.weekly_project_summary_response import WeeklyProjectSummaryResponse, WeeklyProjectSummaryStatus
from backend.src.domain.entities.checked_task_status.task_search_request import TaskSearchRequest
from backend.src.domain.entities.checked_task_status.synthesized_task_status_request import SynthesizedTaskStatusRequest


def _clickup_task(task_id: str = "task-1", name: str = "Build login") -> ClickUpTask:
    """
    Build a ClickUp task DTO for route tests.
    """
    return ClickUpTask(
        id=task_id,
        name=name,
        description="Implement login flow",
        status="done",
        assignee="alice@example.com",
        priority="high",
    )


def test_search_task_route_returns_matches(client: TestClient, container) -> None:
    """
    Test that the task search route returns the matched tasks.
    """
    task = _clickup_task()
    container.task_status_use_case.search_task = AsyncMock(
        return_value=TaskSearchResponse(
            status=TaskSearchStatus.SINGLE_MATCH,
            message="One task found",
            task=[task],
        )
    )

    payload = TaskSearchRequest(space_id="space-1", description="login flow").model_dump()

    response = client.post("/task-status/search", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == TaskSearchStatus.SINGLE_MATCH.value
    assert response.json()["task"][0]["id"] == "task-1"
    container.task_status_use_case.search_task.assert_awaited_once_with(description="login flow", space_id="space-1")


def test_synthesize_task_status_route_returns_result(client: TestClient, container) -> None:
    """
    Test that the synthesis route returns the computed task status.
    """
    container.task_status_use_case.analyze_task_status = AsyncMock(
        return_value=SynthesizedTaskStatusResult(
            is_completed=True,
            confidence="high",
            summary="The task is completed.",
            evidence=["commit linked"],
        )
    )

    payload = SynthesizedTaskStatusRequest(repo_url="https://github.com/org/repo", task=_clickup_task()).model_dump()

    response = client.post("/task-status/synthesize", json=payload)

    assert response.status_code == 200
    assert response.json()["is_completed"] is True
    assert response.json()["confidence"] == "high"
    container.task_status_use_case.analyze_task_status.assert_awaited_once()
    called_task = container.task_status_use_case.analyze_task_status.call_args.kwargs["task"]
    assert called_task.id == "task-1"
    assert container.task_status_use_case.analyze_task_status.call_args.kwargs["repo_url"] == "https://github.com/org/repo"


def test_check_project_status_route_returns_summary(client: TestClient, container) -> None:
    """
    Test that the project status route returns the computed summary.
    """
    container.project_status_use_case.get_project_status = AsyncMock(
        return_value=ProjectStatusSummary(
            status=ProjectStatusCode.FULL,
            message="Healthy project",
            total_tasks=4,
            tasks_summary=[TaskSummary(status="done", percentage=50.0)],
            last_commit=datetime(2024, 1, 2),
            last_deployment=datetime(2024, 1, 3),
            overdue_todo_tasks=[],
            stale_tasks=[],
            unverified_done_tasks=[],
        )
    )

    payload = ProjectSpaceRequest(space_id="space-1", repo_url="https://github.com/org/repo").model_dump()

    response = client.post("/project-status/status", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == ProjectStatusCode.FULL.value
    assert response.json()["total_tasks"] == 4
    container.project_status_use_case.get_project_status.assert_awaited_once_with(
        space_id="space-1",
        repo_url="https://github.com/org/repo",
    )


def test_summarize_weekly_project_route_returns_summary(client: TestClient, container) -> None:
    """
    Test that the weekly summary route returns the computed weekly report.
    """
    container.weekly_project_summarizer_use_case.get_weekly_project_summary = AsyncMock(
        return_value=WeeklyProjectSummaryResponse(
            status=WeeklyProjectSummaryStatus.FULL,
            message="Weekly summary ready",
            created_tasks=[],
            in_progress_tasks=[],
            done_tasks=[_clickup_task("task-2", "Ship release")],
            last_7_days_deployments=[
                DeploymentDTO(
                    dep_id=7,
                    environment="prod",
                    ref="main",
                    sha="abc1234",
                    creator="octo",
                    created_at=datetime(2024, 1, 4),
                    description="release",
                    state="success",
                    log_url="https://example.com/log",
                )
            ],
            deployments_summary="Deployment activity looks good.",
            last_7_days_commits=[
                CommitDTO(
                    sha="abc1234",
                    message="Ship release",
                    author="octo",
                    date=datetime(2024, 1, 4),
                    url="https://github.com/org/repo/commit/abc1234",
                )
            ],
            commits_summary="Commit activity looks good.",
        )
    )

    payload = ProjectSpaceRequest(space_id="space-1", repo_url="https://github.com/org/repo").model_dump()

    response = client.post("/weekly-summary/summary", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == WeeklyProjectSummaryStatus.FULL.value
    assert response.json()["done_tasks"][0]["id"] == "task-2"
    container.weekly_project_summarizer_use_case.get_weekly_project_summary.assert_awaited_once_with(
        space_id="space-1",
        repo_url="https://github.com/org/repo",
    )


def test_find_task_by_commit_route_returns_mapping(client: TestClient, container) -> None:
    """
    Test that the commit mapping route returns the matched task.
    """
    container.commit_task_mapping_use_case.map_commit_task = AsyncMock(
        return_value=MappedCommitTaskResponse(
            status=CommitTaskMappingStatus.FOUND,
            message="Task found",
            task=_clickup_task("task-3", "Fix checkout"),
        )
    )

    response = client.post(
        "/commit-traceability/find-task-by-commit",
        json={"commit": "Fix checkout", "space_id": "space-1"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == CommitTaskMappingStatus.FOUND.value
    assert response.json()["task"]["id"] == "task-3"
    container.commit_task_mapping_use_case.map_commit_task.assert_awaited_once_with(
        commit="Fix checkout",
        space_id="space-1",
    )
