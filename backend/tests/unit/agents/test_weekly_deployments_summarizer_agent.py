from types import SimpleNamespace
from datetime import datetime

from backend.src.infrastructure.external.weekly_project_summarization.weekly_deployments_summarizer_agent import (
    WeeklyDeploymentsSummarizerAgent,
)


def test_weekly_deployments_summarizer_agent_calls_llm_and_returns_summary():
    agent = WeeklyDeploymentsSummarizerAgent(prompt_loader=object())
    # stub _call_llm to return an object with a summary attribute
    agent._call_llm = lambda *a, **k: SimpleNamespace(summary="weekly summary")

    # pass a non-empty deployments list so the LLM path is used
    result = agent.summarize_deployments([SimpleNamespace(created_at=datetime(2024,1,2), environment="prod", ref="main", creator="octo", state="success")])
    assert result == "weekly summary"
