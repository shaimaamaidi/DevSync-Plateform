"""
Unit tests for ClickUpTaskGeneratorFromBacklogAgent.
"""

from unittest.mock import MagicMock

from backend.src.domain.entities.backlog.task import Task
from backend.src.domain.entities.backlog.user_story import UserStory
from backend.src.domain.entities.generated_tasks.generated_task_from_backlog import (
    GeneratedTaskFromBacklog,
    GeneratedTaskListFromBacklog,
)
from backend.src.domain.entities.sprint.estimation import TaskEstimate
from backend.src.domain.entities.sprint.sprint import Sprint, UserStorySprint
from backend.src.infrastructure.external.shared.agents import base_agent
from backend.src.infrastructure.external.task_generation_from_backlog.clickup_task_generator_from_backlog_agent import (
    ClickUpTaskGeneratorFromBacklogAgent,
)


def _patch_base_agent(monkeypatch) -> None:
    """
    Patch BaseAgent initialization for deterministic unit tests.
    """
    def fake_init(self, prompt_loader):
        self.prompt_loader = prompt_loader

    monkeypatch.setattr(base_agent.BaseAgent, "__init__", fake_init)


def _sample_backlog() -> Sprint:
    """
    Build a sprint backlog sample for tests.
    """
    return Sprint(
        name="Sprint 1",
        goal="Ship authentication",
        total_estimated_hours=8,
        user_stories=[
            UserStorySprint(
                user_story=UserStory(title="Login", description="Allow users to sign in."),
                tasks=[TaskEstimate(task=Task(title="Build form", description="Create login form."), estimated_hours=5)],
            )
        ],
    )


def test_generate_tasks_returns_generated_tasks(monkeypatch) -> None:
    """
    Test that the agent returns generated backlog tasks from the parsed LLM response.
    """
    _patch_base_agent(monkeypatch)
    agent = ClickUpTaskGeneratorFromBacklogAgent(MagicMock())
    parsed = GeneratedTaskListFromBacklog(
        tasks=[
            GeneratedTaskFromBacklog(
                task_name="Build login",
                task_description="Implement login flow",
                task_assigne="Alice",
                task_status="To Do",
                task_priority="High",
                location="Backend",
                estimation=5,
            )
        ]
    )
    monkeypatch.setattr(agent, "_call_llm", MagicMock(return_value=parsed))

    result = agent.generate_tasks(
        sprint_backlog=_sample_backlog(),
        locations_statuses={"Backend": {"statuses": ["To Do"], "priorities": ["High"]}},
    )

    assert result == parsed.tasks
    called_variables = agent._call_llm.call_args.kwargs["variables"]
    assert "Sprint: Sprint 1" in called_variables["backlog"]
    assert "Build form" in called_variables["backlog"]


def test_generate_tasks_returns_empty_list_for_empty_result(monkeypatch) -> None:
    """
    Test that the agent returns an empty list when the LLM yields no backlog tasks.
    """
    _patch_base_agent(monkeypatch)
    agent = ClickUpTaskGeneratorFromBacklogAgent(MagicMock())
    monkeypatch.setattr(agent, "_call_llm", MagicMock(return_value=GeneratedTaskListFromBacklog(tasks=[])))

    result = agent.generate_tasks(sprint_backlog=_sample_backlog(), locations_statuses={})

    assert result == []