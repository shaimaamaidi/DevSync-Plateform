from types import SimpleNamespace

from backend.src.infrastructure.external.project_status_checking.stale_task_inspector_agent import (
    StaleTaskInspectorAgent,
)


def test_stale_task_inspector_returns_empty_when_none():
    agent = StaleTaskInspectorAgent(prompt_loader=object())
    agent._call_llm = lambda *a, **k: SimpleNamespace(tasks=[])

    result = agent.inspect_stale_tasks([], [])
    assert result == []
