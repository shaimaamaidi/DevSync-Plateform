"""
Unit tests for SummarizeWeeklyProjectUseCase.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.src.application.use_cases import summarize_weekly_project_use_case as summarize_weekly_project_use_case_module
from backend.src.application.use_cases.summarize_weekly_project_use_case import SummarizeWeeklyProjectUseCase
from backend.src.domain.entities.clickup.folder_with_lists import FolderWithLists
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpList, ClickUpTask
from backend.src.domain.entities.github.commit import CommitDTO
from backend.src.domain.entities.github.deployment import DeploymentDTO
from backend.src.domain.entities.weekly_project_summary.weekly_project_summary_response import WeeklyProjectSummaryStatus


class _FixedDateTime(datetime):
    """
    Deterministic datetime used to freeze the weekly summary window.
    """

    @classmethod
    def now(cls, tz=None):
        return datetime(2024, 1, 8, 12, 0, tzinfo=timezone.utc)


@pytest.mark.asyncio
async def test_get_weekly_project_summary_returns_empty_status_when_no_tasks_and_no_repo(monkeypatch) -> None:
    """
    Test that an empty ClickUp workspace without GitHub returns the no-data status.
    """
    clickup_reader = MagicMock()
    clickup_reader.get_space_full_structure.return_value = []
    weekly_commits_summarizer = MagicMock()
    weekly_deployments_summarizer = MagicMock()
    github_deployment_service = MagicMock()
    github_commit_service = MagicMock()
    use_case = SummarizeWeeklyProjectUseCase(
        clickup_reader,
        weekly_commits_summarizer,
        weekly_deployments_summarizer,
        github_deployment_service,
        github_commit_service,
    )
    fetch_task_context_mock = MagicMock()
    monkeypatch.setattr(summarize_weekly_project_use_case_module, "fetch_task_context", fetch_task_context_mock)

    result = await use_case.get_weekly_project_summary("space-1", None)

    assert result.status == WeeklyProjectSummaryStatus.NO_GITHUB_AND_CLICKUP_EMPTY
    assert result.created_tasks == []
    assert result.last_7_days_commits == []
    assert result.last_7_days_deployments == []
    fetch_task_context_mock.assert_not_called()
    github_commit_service.get_commits_between_dates.assert_not_called()
    github_deployment_service.get_deployments_between_dates.assert_not_called()
    weekly_commits_summarizer.summarize_commits.assert_not_called()
    weekly_deployments_summarizer.summarize_deployments.assert_not_called()


@pytest.mark.asyncio
async def test_get_weekly_project_summary_aggregates_clickup_and_git_history(monkeypatch) -> None:
    """
    Test that the use case aggregates task activity with GitHub activity.
    """
    clickup_reader = MagicMock()
    task_one = ClickUpTask(id="task-1", name="Build login", description="Desc", status="in progress", assignee="alice@example.com", priority="high")
    task_two = ClickUpTask(id="task-2", name="Ship release", description="Desc", status="done", assignee="bob@example.com", priority="high")
    clickup_reader.get_space_full_structure.return_value = [
        FolderWithLists(
            id="folder-1",
            name="Backend",
            lists=[ClickUpList(id="list-1", name="Sprint", tasks=[task_one, task_two], statuses=[], priorities=[])],
        )
    ]

    weekly_commits_summarizer = MagicMock()
    weekly_commits_summarizer.summarize_commits.return_value = "Commit summary"
    weekly_deployments_summarizer = MagicMock()
    weekly_deployments_summarizer.summarize_deployments.return_value = "Deployment summary"
    github_deployment_service = MagicMock()
    github_deployment_service.get_deployments_between_dates = AsyncMock(return_value=[
        DeploymentDTO(
            dep_id=1,
            environment="prod",
            ref="main",
            sha="abc123",
            creator="octo",
            created_at=datetime(2024, 1, 7, 12, 0, tzinfo=timezone.utc),
            description="release",
            state="success",
            log_url="https://example.com/log",
        )
    ])
    github_commit_service = MagicMock()
    github_commit_service.get_commits_between_dates = AsyncMock(return_value=[
        CommitDTO(
            sha="abc123",
            message="Implement login",
            author="octo",
            date=datetime(2024, 1, 7, 12, 0, tzinfo=timezone.utc),
            url="https://github.com/org/repo/commit/abc123",
        )
    ])
    use_case = SummarizeWeeklyProjectUseCase(
        clickup_reader,
        weekly_commits_summarizer,
        weekly_deployments_summarizer,
        github_deployment_service,
        github_commit_service,
    )

    async def fake_fetch_task_context(task, reader):
        contexts = {
            "task-1": {
                "date_created": datetime(2024, 1, 7, 12, 0, tzinfo=timezone.utc),
                "date_closed": None,
                "since_current_status": datetime(2024, 1, 7, 12, 0, tzinfo=timezone.utc),
            },
            "task-2": {
                "date_created": datetime(2024, 1, 7, 12, 0, tzinfo=timezone.utc),
                "date_closed": datetime(2024, 1, 7, 12, 0, tzinfo=timezone.utc),
                "since_current_status": datetime(2024, 1, 7, 12, 0, tzinfo=timezone.utc),
            },
        }
        return task, contexts[task.id]

    monkeypatch.setattr(summarize_weekly_project_use_case_module, "fetch_task_context", fake_fetch_task_context)
    monkeypatch.setattr(summarize_weekly_project_use_case_module.datetime, "datetime", _FixedDateTime)

    result = await use_case.get_weekly_project_summary("space-1", "https://github.com/org/repo")

    assert result.status == WeeklyProjectSummaryStatus.FULL
    assert len(result.created_tasks) == 2
    assert len(result.in_progress_tasks) == 1
    assert len(result.done_tasks) == 1
    assert result.deployments_summary == "Deployment summary"
    assert result.commits_summary == "Commit summary"
    github_deployment_service.get_deployments_between_dates.assert_awaited_once()
    github_commit_service.get_commits_between_dates.assert_awaited_once()
    weekly_commits_summarizer.summarize_commits.assert_called_once()
    weekly_deployments_summarizer.summarize_deployments.assert_called_once()