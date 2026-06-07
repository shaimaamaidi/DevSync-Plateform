from types import SimpleNamespace
import asyncio

from backend.src.infrastructure.external.task_status_checking.task_search_agent import TaskSearchAgent


def test_task_search_agent_returns_empty_when_no_ids():
    agent = TaskSearchAgent(prompt_loader=object())
    agent._call_llm = lambda *a, **k: SimpleNamespace(candidates=[])

    # empty folders -> should return empty list
    result = asyncio.run(agent.search_task("question", []))
    assert result == []
