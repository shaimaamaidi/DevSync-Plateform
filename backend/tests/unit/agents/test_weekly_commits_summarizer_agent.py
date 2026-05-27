from types import SimpleNamespace

from backend.src.infrastructure.external.weekly_project_summarization.weekly_commits_summarizer_agent import (
    WeeklyCommitsSummarizerAgent,
)


def test_weekly_commits_summarizer_agent_calls_llm_and_returns_summary():
    agent = WeeklyCommitsSummarizerAgent(prompt_loader=object())
    agent._call_llm = lambda *a, **k: SimpleNamespace(summary="commits summary")

    result = agent.summarize_commits([])
    assert result == "commits summary"
