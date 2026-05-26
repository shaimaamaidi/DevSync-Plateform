"""
Unit tests for LLM-backed infrastructure agents.
"""

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from backend.src.domain.entities.checked_project_status.inspected_stale_task_result import (
    InspectedStaleTaskListResult,
    InspectedStaleTaskResult,
)
from backend.src.domain.entities.checked_project_status.inspected_unverified_done_task_result import (
    InspectedUnverifiedDoneTaskListResult,
    InspectedUnverifiedDoneTaskResult,
)
from backend.src.domain.entities.checked_task_status.synthesized_task_status_result import SynthesizedTaskStatusResult
from backend.src.domain.entities.checked_task_status.task_search_result import TaskSearchResult
from backend.src.domain.entities.clickup.folder_with_lists import FolderWithLists
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpList, ClickUpTask
from backend.src.domain.entities.github.commit import CommitDTO
from backend.src.domain.entities.github.deployment import DeploymentDTO
from backend.src.domain.entities.weekly_project_summary.weekly_summary_narrative import WeeklySummaryNarrative
from backend.src.infrastructure.external.project_status_checking.stale_task_inspector_agent import StaleTaskInspectorAgent
from backend.src.infrastructure.external.project_status_checking.unverified_done_task_inspector_agent import (
    UnverifiedDoneTaskInspectorAgent,
)
from backend.src.infrastructure.external.shared.agents import base_agent
from backend.src.infrastructure.external.task_status_checking.task_search_agent import TaskSearchAgent
from backend.src.infrastructure.external.task_status_checking.task_status_synthesizer_agent import (
    TaskStatusSynthesizerAgent,
)
from backend.src.infrastructure.external.weekly_project_summarization.weekly_commits_summarizer_agent import (
    WeeklyCommitsSummarizerAgent,
)
from backend.src.infrastructure.external.weekly_project_summarization.weekly_deployments_summarizer_agent import (
    WeeklyDeploymentsSummarizerAgent,
)


class _FakeAzureOpenAI:
    """
    Minimal AzureOpenAI stand-in for agent construction.
    """

    def __init__(self, *args, **kwargs) -> None:
        self.chat = SimpleNamespace(completions=SimpleNamespace(parse=MagicMock()))


def _prepare_agent_env(monkeypatch) -> None:
    """
    Configure the environment required by BaseAgent.
    """
    monkeypatch.setattr(base_agent, "load_dotenv", lambda *args, **kwargs: True)
    monkeypatch.setattr(base_agent, "AzureOpenAI", _FakeAzureOpenAI)
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "key")
    monkeypatch.setenv("AZURE_OPENAI_API_VERSION", "2024-01-01")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")


def _prompt_loader() -> MagicMock:
    """
    Build a prompt loader mock.
    """
    return MagicMock()


def _task(task_id: str = "task-1", name: str = "Build login") -> ClickUpTask:
    """
    Build a ClickUp task for agent tests.
    """
    return ClickUpTask(
        id=task_id,
        name=name,
        description="Implement login flow",
        status="done",
        assignee="alice@example.com",
        priority="high",
    )


def _commit(sha: str = "abc1234") -> CommitDTO:
    """
    Build a GitHub commit DTO for agent tests.
    """
    return CommitDTO(
        sha=sha,
        message="Implement login",
        author="octo",
        date=datetime(2024, 1, 1),
        url="https://github.com/org/repo/commit/abc1234",
    )


def _deployment(dep_id: int = 1) -> DeploymentDTO:
    """
    Build a GitHub deployment DTO for agent tests.
    """
    return DeploymentDTO(
        dep_id=dep_id,
        environment="prod",
        ref="main",
        sha="abc1234",
        creator="octo",
        created_at=datetime(2024, 1, 2),
        description="release",
        state="success",
        log_url="https://example.com/log",
    )


def test_stale_task_inspector_returns_tasks(monkeypatch) -> None:
    """
    Test that stale task inspection returns parsed stale tasks.
    """
    _prepare_agent_env(monkeypatch)
    agent = StaleTaskInspectorAgent(_prompt_loader())
    task = _task()
    commit = _commit()
    expected = [
        InspectedStaleTaskResult(
            task_id="task-1",
            task_name="Build login",
            task_description="Implement login flow",
            is_blocked=True,
            reason="No recent commits",
            confidence="high",
        )
    ]
    monkeypatch.setattr(
        agent,
        "_call_llm",
        MagicMock(return_value=InspectedStaleTaskListResult(tasks=expected)),
    )

    result = agent.inspect_stale_tasks([task], [commit])

    assert result == expected


def test_stale_task_inspector_returns_empty_list_when_no_result(monkeypatch) -> None:
    """
    Test that stale task inspection falls back to an empty list.
    """
    _prepare_agent_env(monkeypatch)
    agent = StaleTaskInspectorAgent(_prompt_loader())
    monkeypatch.setattr(agent, "_call_llm", MagicMock(return_value=InspectedStaleTaskListResult(tasks=[])))

    result = agent.inspect_stale_tasks([_task()], [_commit()])

    assert result == []


def test_unverified_done_task_inspector_returns_tasks(monkeypatch) -> None:
    """
    Test that completed task inspection returns parsed unverified tasks.
    """
    _prepare_agent_env(monkeypatch)
    agent = UnverifiedDoneTaskInspectorAgent(_prompt_loader())
    expected = [
        InspectedUnverifiedDoneTaskResult(
            task_id="task-2",
            task_name="Ship release",
            task_description="Release version 1.0",
            has_commit=False,
            reason="No commit evidence",
            confidence="medium",
        )
    ]
    monkeypatch.setattr(
        agent,
        "_call_llm",
        MagicMock(return_value=InspectedUnverifiedDoneTaskListResult(tasks=expected)),
    )

    result = agent.verify_done_tasks([_task("task-2", "Ship release")], [_commit()])

    assert result == expected


def test_unverified_done_task_inspector_returns_empty_list_when_no_result(monkeypatch) -> None:
    """
    Test that completed task inspection falls back to an empty list.
    """
    _prepare_agent_env(monkeypatch)
    agent = UnverifiedDoneTaskInspectorAgent(_prompt_loader())
    monkeypatch.setattr(agent, "_call_llm", MagicMock(return_value=InspectedUnverifiedDoneTaskListResult(tasks=[])))

    result = agent.verify_done_tasks([_task()], [_commit()])

    assert result == []


def test_task_search_agent_returns_matching_tasks(monkeypatch) -> None:
    """
    Test that task search returns the matched ClickUp tasks.
    """
    _prepare_agent_env(monkeypatch)
    agent = TaskSearchAgent(_prompt_loader())
    task = _task()
    folder = FolderWithLists(
        id="folder-1",
        name="Backend",
        lists=[ClickUpList(id="list-1", name="Sprint", tasks=[task], statuses=[], priorities=[])],
    )
    monkeypatch.setattr(agent, "_call_llm", MagicMock(return_value=TaskSearchResult(ids=["task-1"])))

    result = agent.search_task("login flow", [folder])

    assert result == [task]


def test_task_search_agent_returns_empty_list_when_no_ids(monkeypatch) -> None:
    """
    Test that task search falls back to an empty list.
    """
    _prepare_agent_env(monkeypatch)
    agent = TaskSearchAgent(_prompt_loader())
    folder = FolderWithLists(
        id="folder-1",
        name="Backend",
        lists=[ClickUpList(id="list-1", name="Sprint", tasks=[_task()], statuses=[], priorities=[])],
    )
    monkeypatch.setattr(agent, "_call_llm", MagicMock(return_value=TaskSearchResult(ids=[])))

    result = agent.search_task("login flow", [folder])

    assert result == []


def test_task_status_synthesizer_returns_result(monkeypatch) -> None:
    """
    Test that task status synthesis returns the parsed result.
    """
    _prepare_agent_env(monkeypatch)
    agent = TaskStatusSynthesizerAgent(_prompt_loader())
    task = _task()
    expected = SynthesizedTaskStatusResult(
        is_completed=True,
        confidence="high",
        summary="Task completed.",
        evidence=["commit linked"],
    )
    monkeypatch.setattr(agent, "_call_llm", MagicMock(return_value=expected))

    result = agent.synthesize_task_status(task, [_deployment()], [_commit()], {"signal": True})

    assert result == expected


def test_task_status_synthesizer_returns_fallback_when_no_result(monkeypatch) -> None:
    """
    Test that task status synthesis falls back to ClickUp status.
    """
    _prepare_agent_env(monkeypatch)
    agent = TaskStatusSynthesizerAgent(_prompt_loader())
    task = _task()
    monkeypatch.setattr(agent, "_call_llm", MagicMock(return_value=None))

    result = agent.synthesize_task_status(task, [], [], {})

    assert result.is_completed is True
    assert result.confidence == "low"
    assert "ClickUp status only" in result.summary


def test_weekly_commits_summarizer_returns_summary(monkeypatch) -> None:
    """
    Test that weekly commits summarization returns the narrative summary.
    """
    _prepare_agent_env(monkeypatch)
    agent = WeeklyCommitsSummarizerAgent(_prompt_loader())
    monkeypatch.setattr(agent, "_call_llm", MagicMock(return_value=WeeklySummaryNarrative(summary="Delivered login flow.")))

    result = agent.summarize_commits([_commit()])

    assert result == "Delivered login flow."


def test_weekly_commits_summarizer_returns_empty_string_when_no_summary(monkeypatch) -> None:
    """
    Test that weekly commits summarization falls back to an empty string.
    """
    _prepare_agent_env(monkeypatch)
    agent = WeeklyCommitsSummarizerAgent(_prompt_loader())
    monkeypatch.setattr(agent, "_call_llm", MagicMock(return_value=None))

    result = agent.summarize_commits([_commit()])

    assert result == ""


def test_weekly_deployments_summarizer_returns_summary(monkeypatch) -> None:
    """
    Test that weekly deployments summarization returns the narrative summary.
    """
    _prepare_agent_env(monkeypatch)
    agent = WeeklyDeploymentsSummarizerAgent(_prompt_loader())
    monkeypatch.setattr(agent, "_call_llm", MagicMock(return_value=WeeklySummaryNarrative(summary="Released v1.0.")))

    result = agent.summarize_deployments([_deployment()])

    assert result == "Released v1.0."


def test_weekly_deployments_summarizer_returns_empty_string_when_no_summary(monkeypatch) -> None:
    """
    Test that weekly deployments summarization falls back to an empty string.
    """
    _prepare_agent_env(monkeypatch)
    agent = WeeklyDeploymentsSummarizerAgent(_prompt_loader())
    monkeypatch.setattr(agent, "_call_llm", MagicMock(return_value=None))

    result = agent.summarize_deployments([_deployment()])

    assert result == ""