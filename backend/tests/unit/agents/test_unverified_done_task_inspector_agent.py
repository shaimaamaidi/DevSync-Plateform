from types import SimpleNamespace

from backend.src.infrastructure.external.project_status_checking.unverified_done_task_inspector_agent import (
    UnverifiedDoneTaskInspectorAgent,
)


def test_unverified_done_task_inspector_returns_empty_when_none():
    agent = UnverifiedDoneTaskInspectorAgent(prompt_loader=object())
    agent._call_llm = lambda *a, **k: SimpleNamespace(tasks=[])

    result = agent.verify_done_tasks([], [])
    assert result == []
