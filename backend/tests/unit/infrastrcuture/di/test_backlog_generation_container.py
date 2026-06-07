"""
Unit tests for BacklogGenerationContainer.
"""

from unittest.mock import MagicMock

from backend.src.infrastructure.di import backlog_generation_container
from backend.src.infrastructure.di.backlog_generation_container import BacklogGenerationContainer


def _patch_base_containers(monkeypatch) -> None:
    """
    Patch base container initialization to avoid constructing real services.
    """
    def fake_ai_init(self) -> None:
        self.prompt_loader = MagicMock(name="prompt_loader")

    monkeypatch.setattr(backlog_generation_container.BaseAIContainer, "__init__", fake_ai_init)


def _patch_dependencies(monkeypatch) -> dict[str, MagicMock]:
    """
    Patch backlog dependencies with lightweight mocks.
    """
    mocks = {
        "epic_generator": MagicMock(name="epic_generator"),
        "user_story_generator": MagicMock(name="user_story_generator"),
        "task_generator": MagicMock(name="task_generator"),
        "backlog_cleaner": MagicMock(name="backlog_cleaner"),
        "backlog_prioritizer": MagicMock(name="backlog_prioritizer"),
        "sprint_planner": MagicMock(name="sprint_planner"),
        "product_context_builder": MagicMock(name="product_context_builder"),
        "market_intelligence_summarizer": MagicMock(name="market_intelligence_summarizer"),
        "market_intelligence_validator": MagicMock(name="market_intelligence_validator"),
        "market_query_generator": MagicMock(name="market_query_generator"),
        "user_backlog_fixer": MagicMock(name="user_backlog_fixer"),
        "web_search": MagicMock(name="web_search"),
        "backlog_orchestrator_agent": MagicMock(name="backlog_orchestrator_agent"),
        "product_context_tool": MagicMock(name="product_context_tool"),
        "market_query_tool": MagicMock(name="market_query_tool"),
        "web_search_tool": MagicMock(name="web_search_tool"),
        "market_summary_tool": MagicMock(name="market_summary_tool"),
        "market_validation_tool": MagicMock(name="market_validation_tool"),
        "backlog_generation_tool": MagicMock(name="backlog_generation_tool"),
        "user_backlog_fixer_tool": MagicMock(name="user_backlog_fixer_tool"),
        "delivery_planning_tool": MagicMock(name="delivery_planning_tool"),
    }

    monkeypatch.setattr(backlog_generation_container, "EpicGeneratorAgent", lambda prompt_loader: mocks["epic_generator"])
    monkeypatch.setattr(backlog_generation_container, "UserStoryGeneratorAgent", lambda prompt_loader: mocks["user_story_generator"])
    monkeypatch.setattr(backlog_generation_container, "TaskGeneratorAgent", lambda prompt_loader: mocks["task_generator"])
    monkeypatch.setattr(backlog_generation_container, "EpicCleanerAgent", lambda prompt_loader: mocks["backlog_cleaner"])
    monkeypatch.setattr(backlog_generation_container, "BacklogPrioritizerAgent", lambda prompt_loader: mocks["backlog_prioritizer"])
    monkeypatch.setattr(backlog_generation_container, "SprintPlannerOrchestrator", lambda prompt_loader, *args, **kwargs: mocks["sprint_planner"])
    monkeypatch.setattr(backlog_generation_container, "ProductContextBuilderAgent", lambda prompt_loader: mocks["product_context_builder"])
    monkeypatch.setattr(backlog_generation_container, "MarketIntelligenceSummarizerAgent", lambda prompt_loader: mocks["market_intelligence_summarizer"])
    monkeypatch.setattr(backlog_generation_container, "MarketIntelligenceValidatorAgent", lambda prompt_loader: mocks["market_intelligence_validator"])
    monkeypatch.setattr(backlog_generation_container, "MarketQueryGeneratorAgent", lambda prompt_loader: mocks["market_query_generator"])
    monkeypatch.setattr(backlog_generation_container, "UserBacklogFixerAgent", lambda prompt_loader: mocks["user_backlog_fixer"])
    monkeypatch.setattr(backlog_generation_container, "WebSearchAgent", lambda: mocks["web_search"])
    monkeypatch.setattr(backlog_generation_container, "BacklogGenerationOrchestratorAgent", lambda **kwargs: mocks["backlog_orchestrator_agent"])
    monkeypatch.setattr(backlog_generation_container, "ProductContextBuilderTool", lambda agent: mocks["product_context_tool"])
    monkeypatch.setattr(backlog_generation_container, "MarketQueryGeneratorTool", lambda agent: mocks["market_query_tool"])
    monkeypatch.setattr(backlog_generation_container, "WebSearchTool", lambda agent: mocks["web_search_tool"])
    monkeypatch.setattr(backlog_generation_container, "MarketSummarizerTool", lambda agent: mocks["market_summary_tool"])
    monkeypatch.setattr(backlog_generation_container, "MarketValidatorTool", lambda agent: mocks["market_validation_tool"])
    monkeypatch.setattr(backlog_generation_container, "BacklogGeneratorTool", lambda agent: mocks["backlog_generation_tool"])
    monkeypatch.setattr(backlog_generation_container, "UserBacklogFixerTool", lambda agent: mocks["user_backlog_fixer_tool"])
    monkeypatch.setattr(backlog_generation_container, "DeliveryPlannerTool", lambda backlog_prioritizer, sprint_planner: mocks["delivery_planning_tool"])

    return mocks


def test_backlog_generation_container_initializes_agents_and_tools(monkeypatch) -> None:
    """
    Test that the backlog container wires agents and tools.
    """
    _patch_base_containers(monkeypatch)
    mocks = _patch_dependencies(monkeypatch)

    container = BacklogGenerationContainer()

    assert container.epic_generator_agent is mocks["epic_generator"]
    assert container.backlog_generation_orchestrator_agent is mocks["backlog_orchestrator_agent"]
    assert container.web_search_agent is mocks["web_search"]
    assert container.product_context_tool is mocks["product_context_tool"]
    assert container.delivery_planning_tool is mocks["delivery_planning_tool"]
    assert container.generate_backlog_use_case is None
    assert isinstance(container.generate_backlog_use_case, type(None))