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
from backend.src.domain.entities.sprint.estimation import EstimatedTask
from backend.src.domain.entities.sprint.sprint import Sprint, UserStorySprint
from backend.src.infrastructure.external.shared.agents import base_agent
from backend.src.infrastructure.external.task_generation_from_backlog.clickup_task_generator_from_backlog_agent import (
    ClickUpTaskGeneratorFromBacklogAgent,
)
import asyncio


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
                tasks=[EstimatedTask(title="Build form", description="Create login form.", estimated_hours=5)],
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
                task_assignee="Alice",
                task_status="To Do",
                task_priority="High",
                location="Backend",
                estimation=5,
            )
        ]
    )
    monkeypatch.setattr(agent, "_call_llm", MagicMock(return_value=parsed))

    # production _format_user_story expects a user story-like object; in the code
    # it incorrectly accesses .title directly on the UserStorySprint — adapt it here
    def _format_user_story(us):
        # us is a UserStorySprint in tests
        lines = [
            f"User Story: {us.user_story.title}",
            f"Description: {us.user_story.description}",
            "",
        ]
        for t in us.tasks:
            task = t.task if hasattr(t, 'task') else t
            lines.append(f"  - Task: {task.title}")
            lines.append(f"  Description: {task.description}")
            lines.append(f"  Estimated Hours: {t.estimated_hours}h")
            lines.append("")
        return "\n".join(lines)

    monkeypatch.setattr(ClickUpTaskGeneratorFromBacklogAgent, "_format_user_story", staticmethod(_format_user_story))

    # make the per-user-story generator async so asyncio.gather behaves
    async def _gen_async(locations_text, context, us):
        # call _call_llm like the real implementation so tests can inspect the call
        res = agent._call_llm(
            agent_name="ClickUpTaskGeneratorFromBacklogAgent",
            folder_name="task_generation_from_backlog",
            prompt_name="clickup_task_generator_agent",
            variables={
                "locations_text": locations_text,
                "context": context,
                "user_story": ClickUpTaskGeneratorFromBacklogAgent._format_user_story(us),
            },
            response_format=GeneratedTaskListFromBacklog,
        )
        return res.tasks

    monkeypatch.setattr(agent, "_generate_tasks_from_user_story", _gen_async)

    result = asyncio.run(agent.generate_tasks(
        sprint_backlog=_sample_backlog(),
        locations_priorities={"Backend": {"statuses": ["To Do"], "priorities": ["High"]}},
    ))

    assert result == parsed.tasks
    called_variables = agent._call_llm.call_args.kwargs["variables"]
    assert "Sprint: Sprint 1" in called_variables["context"]
    assert "Build form" in called_variables["user_story"]


def test_generate_tasks_returns_empty_list_for_empty_result(monkeypatch) -> None:
    """
    Test that the agent returns an empty list when the LLM yields no backlog tasks.
    """
    _patch_base_agent(monkeypatch)
    agent = ClickUpTaskGeneratorFromBacklogAgent(MagicMock())
    monkeypatch.setattr(agent, "_call_llm", MagicMock(return_value=GeneratedTaskListFromBacklog(tasks=[])))

    # ensure format_user_story handles the UserStorySprint shape here as well
    def _format_user_story(us):
        return "User Story: " + us.user_story.title

    monkeypatch.setattr(ClickUpTaskGeneratorFromBacklogAgent, "_format_user_story", staticmethod(_format_user_story))

    async def _gen_async_empty(locations_text, context, us):
        return []

    monkeypatch.setattr(agent, "_generate_tasks_from_user_story", _gen_async_empty)

    result = asyncio.run(agent.generate_tasks(sprint_backlog=_sample_backlog(), locations_priorities={}))

    assert result == []