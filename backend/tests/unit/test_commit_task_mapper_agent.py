"""
Unit tests for CommitTaskMapperAgent.
"""

from unittest.mock import MagicMock

from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.mapped_commit_task.mapped_commit_task_result import CommitTaskMapperResult
from backend.src.infrastructure.external.commit_task_mapping.commit_task_mapper_agent import CommitTaskMapperAgent
from backend.src.infrastructure.external.shared.agents import base_agent


def _patch_base_agent(monkeypatch) -> None:
    """
    Patch BaseAgent initialization for deterministic unit tests.
    """
    def fake_init(self, prompt_loader):
        self.prompt_loader = prompt_loader

    monkeypatch.setattr(base_agent.BaseAgent, "__init__", fake_init)


def test_map_commit_task_returns_matched_task(monkeypatch) -> None:
    """
    Test that the agent returns the matching task when the LLM selects a valid id.
    """
    _patch_base_agent(monkeypatch)
    prompt_loader = MagicMock()
    agent = CommitTaskMapperAgent(prompt_loader)
    task_one = ClickUpTask(id="task-1", name="Build login", description="Desc", status="done", assignee="alice@example.com", priority="high")
    task_two = ClickUpTask(id="task-2", name="Ship release", description="Desc", status="done", assignee="bob@example.com", priority="high")
    monkeypatch.setattr(agent, "_call_llm", MagicMock(return_value=CommitTaskMapperResult(id="task-2")))

    result = agent.map_commit_task("fix login", [task_one, task_two])

    assert result == task_two
    called_variables = agent._call_llm.call_args.kwargs["variables"]
    assert called_variables["commit"] == "fix login"
    assert "Build login" in called_variables["tasks"]


def test_map_commit_task_returns_none_for_missing_match(monkeypatch) -> None:
    """
    Test that the agent returns None when the LLM result does not match an input task.
    """
    _patch_base_agent(monkeypatch)
    prompt_loader = MagicMock()
    agent = CommitTaskMapperAgent(prompt_loader)
    task = ClickUpTask(id="task-1", name="Build login", description="Desc", status="done", assignee="alice@example.com", priority="high")
    monkeypatch.setattr(agent, "_call_llm", MagicMock(return_value=CommitTaskMapperResult(id="missing-task")))

    result = agent.map_commit_task("fix login", [task])

    assert result is None