"""
Unit tests for WeeklyProjectSummarizationContainer.
"""

from unittest.mock import MagicMock

from backend.src.application.use_cases.summarize_weekly_project_use_case import SummarizeWeeklyProjectUseCase
from backend.src.infrastructure.di import weekly_project_summary_container
from backend.src.infrastructure.di.weekly_project_summary_container import WeeklyProjectSummarizationContainer


def _patch_base_containers(monkeypatch) -> None:
    """
    Patch the base container initializers to avoid creating real external services.
    """
    def fake_ai_init(self) -> None:
        self.prompt_loader = MagicMock(name="prompt_loader")

    def fake_clickup_init(self) -> None:
        self.http_client = MagicMock(name="http_client")
        self.clickup_reader = MagicMock(name="clickup_reader")
        self.clickup_writer = MagicMock(name="clickup_writer")

    def fake_github_init(self) -> None:
        self.github_deployment_service = MagicMock(name="github_deployment_service")
        self.github_commit_service = MagicMock(name="github_commit_service")

    monkeypatch.setattr(weekly_project_summary_container.BaseAIContainer, "__init__", fake_ai_init)
    monkeypatch.setattr(weekly_project_summary_container.BaseClickUpContainer, "__init__", fake_clickup_init)
    monkeypatch.setattr(weekly_project_summary_container.BaseGitHubContainer, "__init__", fake_github_init)


def test_weekly_project_summary_container_initializes_use_case(monkeypatch) -> None:
    """
    Test that the weekly summary container wires the summary use case.
    """
    _patch_base_containers(monkeypatch)

    deployments_agent = MagicMock(name="deployments_agent")
    commits_agent = MagicMock(name="commits_agent")
    monkeypatch.setattr(weekly_project_summary_container, "WeeklyDeploymentsSummarizerAgent", lambda prompt_loader: deployments_agent)
    monkeypatch.setattr(weekly_project_summary_container, "WeeklyCommitsSummarizerAgent", lambda prompt_loader: commits_agent)

    container = WeeklyProjectSummarizationContainer()

    assert isinstance(container.weekly_project_summarizer_use_case, SummarizeWeeklyProjectUseCase)
    assert container.deployments_summarizer_agent is deployments_agent
    assert container.commits_summarizer_agent is commits_agent
