from types import SimpleNamespace

from backend.src.infrastructure.external.weekly_project_summarization.weekly_deployments_summarizer_agent import (
    WeeklyDeploymentsSummarizerAgent,
)


def test_weekly_deployments_summarizer_agent_calls_llm_and_returns_summary():
    agent = WeeklyDeploymentsSummarizerAgent(prompt_loader=object())
    # stub _call_llm to return an object with a summary attribute
    agent._call_llm = lambda *a, **k: SimpleNamespace(summary="weekly summary")

    # call with empty deployments list — should return the stubbed summary
    result = agent.summarize_deployments([])
    assert result == "weekly summary"
