"""
Integration tests for weekly project summary routes.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.github.commit import CommitDTO
from backend.src.domain.entities.github.deployment import DeploymentDTO
from backend.src.domain.entities.weekly_project_summary.weekly_project_summary_response import (
    WeeklyProjectSummaryResponse,
    WeeklyProjectSummaryStatus,
)


def test_summarize_weekly_project(client: TestClient, container) -> None:
    """
    Test generating a weekly project summary through the API.
    """
    container.weekly_project_summarizer_use_case.get_weekly_project_summary = AsyncMock(return_value=WeeklyProjectSummaryResponse(
        status=WeeklyProjectSummaryStatus.FULL,
        message="Weekly summary generated.",
        created_tasks=[
            ClickUpTask(id="task-1", name="Build login", description="Implement login", status="done", assignee="alice@example.com", priority="high")
        ],
        in_progress_tasks=[],
        done_tasks=[],
        last_7_days_deployments=[
            DeploymentDTO(
                dep_id=1,
                environment="prod",
                ref="main",
                sha="abc123",
                creator="octo",
                created_at=datetime(2024, 1, 7, tzinfo=timezone.utc),
                description="release",
                state="success",
                log_url="https://example.com/log",
            )
        ],
        deployments_summary="Deployment summary",
        last_7_days_commits=[
            CommitDTO(
                sha="abc123",
                message="Implement login",
                author="octo",
                date=datetime(2024, 1, 7, tzinfo=timezone.utc),
                url="https://github.com/org/repo/commit/abc123",
            )
        ],
        commits_summary="Commit summary",
    ))

    response = client.post("/weekly-summary/summary", json={"space_id": "space-1", "repo_url": "https://github.com/org/repo"})

    assert response.status_code == 200
    assert response.json()["status"] == "FULL"
    assert response.json()["deployments_summary"] == "Deployment summary"
    container.weekly_project_summarizer_use_case.get_weekly_project_summary.assert_called_once_with(
        space_id="space-1",
        repo_url="https://github.com/org/repo",
    )