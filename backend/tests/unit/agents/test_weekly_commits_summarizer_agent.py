from types import SimpleNamespace

from backend.src.infrastructure.external.weekly_project_summarization.weekly_commits_summarizer_agent import (
    WeeklyCommitsSummarizerAgent,
)


def test_weekly_commits_summarizer_agent_calls_llm_and_returns_summary():
    agent = WeeklyCommitsSummarizerAgent(prompt_loader=object())
    agent._call_llm = lambda *a, **k: SimpleNamespace(summary="commits summary")

    # must pass a non-empty commits list to invoke the LLM path
    result = agent.summarize_commits([SimpleNamespace(message="m", author="a", date=None)])
    assert result == "commits summary"
