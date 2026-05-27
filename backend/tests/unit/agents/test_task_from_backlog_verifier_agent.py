from types import SimpleNamespace

from backend.src.infrastructure.external.task_verification.task_from_backlog_verifier_agent import (
    TaskFromBacklogVerifierAgent,
)


def test_task_from_backlog_verifier_returns_empty_when_llm_no_results():
    agent = TaskFromBacklogVerifierAgent(prompt_loader=object())
    agent._call_llm = lambda *a, **k: SimpleNamespace(results=[])

    filtered = agent.verify_tasks([], [])
    assert filtered == []
