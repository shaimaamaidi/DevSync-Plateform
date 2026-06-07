"""
Unit tests for ClickUpTaskFromSummaryGeneratorAgent.
"""

from unittest.mock import MagicMock

from backend.src.domain.entities.generated_tasks.generated_task_from_summary import (
    GeneratedTaskFromSummary,
    GeneratedTaskListFromSummary,
)
from backend.src.infrastructure.external.shared.agents import base_agent
from backend.src.infrastructure.external.task_generation_from_summary.clickup_task_generator_from_summary_agent import (
    ClickUpTaskFromSummaryGeneratorAgent,
)


def _patch_base_agent(monkeypatch) -> None:
    """
    Patch BaseAgent initialization for deterministic unit tests.
    """
    def fake_init(self, prompt_loader):
        self.prompt_loader = prompt_loader

    monkeypatch.setattr(base_agent.BaseAgent, "__init__", fake_init)


def test_generate_tasks_returns_generated_tasks(monkeypatch) -> None:
    """
    Test that the agent returns generated tasks from the parsed LLM response.
    """
    _patch_base_agent(monkeypatch)
    agent = ClickUpTaskFromSummaryGeneratorAgent(MagicMock())
    parsed = GeneratedTaskListFromSummary(
        tasks=[
            GeneratedTaskFromSummary(
                task_name="Build login",
                task_description="Implement login flow",
                task_assignee="Alice",
                task_status="To Do",
                task_priority="High",
                location="Backend",
            )
        ]
    )
    monkeypatch.setattr(agent, "_call_llm", MagicMock(return_value=parsed))

    result = agent.generate_tasks(
        meeting_summary="Discussed login and onboarding",
        locations_statuses={"Backend": {"statuses": ["To Do"], "priorities": ["High"]}},
    )

    assert result == parsed.tasks
    called_variables = agent._call_llm.call_args.kwargs["variables"]
    assert called_variables["meeting_summary"] == "Discussed login and onboarding"
    assert "Backend" in called_variables["locations_text"]


def test_generate_tasks_returns_empty_list_for_empty_result(monkeypatch) -> None:
    """
    Test that the agent returns an empty list when the LLM yields no tasks.
    """
    _patch_base_agent(monkeypatch)
    agent = ClickUpTaskFromSummaryGeneratorAgent(MagicMock())
    monkeypatch.setattr(agent, "_call_llm", MagicMock(return_value=GeneratedTaskListFromSummary(tasks=[])))

    result = agent.generate_tasks(meeting_summary="Summary", locations_statuses={})

    assert result == []