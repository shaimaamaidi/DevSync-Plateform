from types import SimpleNamespace

from backend.src.infrastructure.external.task_verification.task_from_summary_verifier_agent import (
    TaskFromSummaryVerifierAgent,
)


def test_task_from_summary_verifier_returns_empty_when_llm_no_results():
    agent = TaskFromSummaryVerifierAgent(prompt_loader=object())
    agent._call_llm = lambda *a, **k: SimpleNamespace(results=[])

    # no existing tasks, no generated tasks -> should return empty list
    filtered = agent.verify_tasks([], [])
    assert filtered == []
