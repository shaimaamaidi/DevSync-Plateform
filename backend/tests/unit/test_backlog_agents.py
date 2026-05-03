"""
Unit tests for backlog agents (happy path + runtime errors).
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from backend.src.domain.entities.backlog.structure import BacklogStructure, EpicBacklog, UserStoryWithTasks
from backend.src.domain.entities.backlog.validation import BacklogValidation
from backend.src.domain.entities.backlog.epic import Epic, EpicList
from backend.src.domain.entities.backlog.task import Task, TaskList
from backend.src.domain.entities.backlog.user_story import UserStory, UserStoryList
from backend.src.domain.entities.market.intelligence import MarketIntelligenceSummary
from backend.src.domain.entities.market.query import QueryGeneration
from backend.src.domain.entities.market.refined_intelligence import RefinedMarketIntelligenceSummary
from backend.src.domain.entities.product.initial_description import InitialDescription
from backend.src.domain.entities.sprint.planning import SprintPlanning
from backend.src.domain.exceptions.backlog.backlog_generation_exception import BacklogGenerationException
from backend.src.domain.exceptions.llm.llm_parsing_exception import LLMParsingException
from backend.src.infrastructure.external.backlog_generation.agents.backlog_cleaner_agent import BacklogCleanerAgent
from backend.src.infrastructure.external.backlog_generation.agents.backlog_generation_orchestrator_agent import (
    BacklogGenerationOrchestratorAgent,
)
from backend.src.infrastructure.external.backlog_generation.agents.backlog_prioritizer_agent import (
    BacklogPrioritizerAgent,
)
from backend.src.infrastructure.external.backlog_generation.agents.epic_generator_agent import EpicGeneratorAgent
from backend.src.infrastructure.external.backlog_generation.agents.market_intelligence_summarizer_agent import (
    MarketIntelligenceSummarizerAgent,
)
from backend.src.infrastructure.external.backlog_generation.agents.market_intelligence_validator_agent import (
    MarketIntelligenceValidatorAgent,
)
from backend.src.infrastructure.external.backlog_generation.agents.market_query_generator_agent import (
    MarketQueryGeneratorAgent,
)
from backend.src.infrastructure.external.backlog_generation.agents.product_context_builder_agent import (
    ProductContextBuilderAgent,
)
from backend.src.infrastructure.external.backlog_generation.agents.sprint_planner_agent import SprintPlannerAgent
from backend.src.infrastructure.external.backlog_generation.agents.task_generator_agent import TaskGeneratorAgent
from backend.src.infrastructure.external.backlog_generation.agents.user_backlog_fixer_agent import UserBacklogFixerAgent
from backend.src.infrastructure.external.backlog_generation.agents.user_story_generator_agent import (
    UserStoryGeneratorAgent,
)
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent


def _prompt_loader():
    loader = MagicMock()
    loader.get_messages.return_value = {"system": "sys", "user": "usr"}
    return loader


def _fake_client(parsed):
    completion = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(parsed=parsed))])
    parse = MagicMock(return_value=completion)
    client = SimpleNamespace(
        beta=SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(parse=parse)))
    )
    return client, parse


def _patch_base_agent(monkeypatch, prompt_loader, parsed=None, raise_exc: Exception | None = None):
    def _fake_init(self, _loader):
        self.prompt_loader = prompt_loader
        self.model = "model"
        if raise_exc:
            def _raise(*_args, **_kwargs):
                raise raise_exc
            completion = SimpleNamespace(choices=[])
            parse = MagicMock(side_effect=_raise)
            self.client = SimpleNamespace(
                beta=SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(parse=parse)))
            )
        else:
            self.client, _ = _fake_client(parsed)

    monkeypatch.setattr(BaseAgent, "__init__", _fake_init)


def _initial_description() -> InitialDescription:
    return InitialDescription(
        product_overview="CRM",
        target_users=["sales"],
        core_features=["pipeline"],
        business_goals=["retention"],
        constraints=["gdpr"],
        summary="Summary",
    )


def _refined_context() -> RefinedMarketIntelligenceSummary:
    return RefinedMarketIntelligenceSummary(
        refined_market_trends="Trends",
        refined_competitor_features=["feat"],
        refined_user_pain_points=["pain"],
        refined_best_practices=["best"],
        refined_enrichment_notes="notes",
        cause="",
        is_valid=True,
    )


def _market_context() -> MarketIntelligenceSummary:
    return MarketIntelligenceSummary(
        market_trends="Trends",
        competitor_features=["feat"],
        user_pain_points=["pain"],
        best_practices=["best"],
        enrichment_notes="notes",
    )


def _backlog_structure() -> BacklogStructure:
    return BacklogStructure(
        epics=[
            EpicBacklog(
                epic=Epic(title="Epic", description="Desc"),
                user_stories=[
                    UserStoryWithTasks(
                        user_story=UserStory(title="Story", description="Desc"),
                        tasks=[Task(title="Task", description="Desc")],
                    )
                ],
            )
        ]
    )


def _backlog_validation() -> BacklogValidation:
    return BacklogValidation(
        is_valid=True,
        corrections=[],
        corrected_backlog=_backlog_structure(),
    )


def test_epic_generator_agent_happy_path(monkeypatch) -> None:
    prompt_loader = _prompt_loader()
    parsed = EpicList(epics=[Epic(title="Epic", description="Desc")])
    _patch_base_agent(monkeypatch, prompt_loader, parsed=parsed)

    agent = EpicGeneratorAgent(prompt_loader)
    result = agent.generate_epics(_initial_description(), _refined_context())

    assert result.epics[0].title == "Epic"


def test_epic_generator_agent_wraps_error(monkeypatch) -> None:
    prompt_loader = _prompt_loader()
    _patch_base_agent(monkeypatch, prompt_loader, raise_exc=RuntimeError("fail"))

    agent = EpicGeneratorAgent(prompt_loader)

    with pytest.raises(LLMParsingException):
        agent.generate_epics(_initial_description(), _refined_context())


def test_user_story_generator_agent_sets_epic_title(monkeypatch) -> None:
    prompt_loader = _prompt_loader()
    parsed = UserStoryList(epic_title="Epic", user_stories=[UserStory(title="Story", description="Desc")])
    _patch_base_agent(monkeypatch, prompt_loader, parsed=parsed)

    agent = UserStoryGeneratorAgent(prompt_loader)
    epic = Epic(title="Epic", description="Desc")
    result = agent.generate_user_stories_by_epic(epic, _initial_description(), _refined_context())

    assert result.epic_title == "Epic"


def test_user_story_generator_agent_wraps_error(monkeypatch) -> None:
    prompt_loader = _prompt_loader()
    _patch_base_agent(monkeypatch, prompt_loader, raise_exc=RuntimeError("fail"))

    agent = UserStoryGeneratorAgent(prompt_loader)

    with pytest.raises(LLMParsingException):
        agent.generate_user_stories_by_epic(
            Epic(title="Epic", description="Desc"),
            _initial_description(),
            _refined_context(),
        )


def test_task_generator_agent_sets_story_title(monkeypatch) -> None:
    prompt_loader = _prompt_loader()
    parsed = TaskList(user_story_title="Story", tasks=[Task(title="Task", description="Desc")])
    _patch_base_agent(monkeypatch, prompt_loader, parsed=parsed)

    agent = TaskGeneratorAgent(prompt_loader)
    story = UserStory(title="Story", description="Desc")
    result = agent.generate_tasks_by_user_story(story, _initial_description(), _refined_context())

    assert result.user_story_title == "Story"


def test_task_generator_agent_wraps_error(monkeypatch) -> None:
    prompt_loader = _prompt_loader()
    _patch_base_agent(monkeypatch, prompt_loader, raise_exc=RuntimeError("fail"))

    agent = TaskGeneratorAgent(prompt_loader)

    with pytest.raises(LLMParsingException):
        agent.generate_tasks_by_user_story(
            UserStory(title="Story", description="Desc"),
            _initial_description(),
            _refined_context(),
        )


def test_product_context_builder_agent_happy_path(monkeypatch) -> None:
    prompt_loader = _prompt_loader()
    parsed = _initial_description()
    _patch_base_agent(monkeypatch, prompt_loader, parsed=parsed)

    agent = ProductContextBuilderAgent(prompt_loader)
    result = agent.build_context("raw")

    assert result.product_overview == "CRM"


def test_product_context_builder_agent_wraps_error(monkeypatch) -> None:
    prompt_loader = _prompt_loader()
    _patch_base_agent(monkeypatch, prompt_loader, raise_exc=RuntimeError("fail"))

    agent = ProductContextBuilderAgent(prompt_loader)

    with pytest.raises(LLMParsingException):
        agent.build_context("raw")


def test_market_query_generator_agent_happy_path(monkeypatch) -> None:
    prompt_loader = _prompt_loader()
    parsed = QueryGeneration(queries=["q1", "q2"])
    _patch_base_agent(monkeypatch, prompt_loader, parsed=parsed)

    agent = MarketQueryGeneratorAgent(prompt_loader)
    result = agent.generate_queries(_initial_description())

    assert result.queries[0] == "q1"


def test_market_query_generator_agent_wraps_error(monkeypatch) -> None:
    prompt_loader = _prompt_loader()
    _patch_base_agent(monkeypatch, prompt_loader, raise_exc=RuntimeError("fail"))

    agent = MarketQueryGeneratorAgent(prompt_loader)

    with pytest.raises(LLMParsingException):
        agent.generate_queries(_initial_description())


def test_market_summarizer_agent_happy_path(monkeypatch) -> None:
    prompt_loader = _prompt_loader()
    parsed = _market_context()
    _patch_base_agent(monkeypatch, prompt_loader, parsed=parsed)

    agent = MarketIntelligenceSummarizerAgent(prompt_loader)
    result = agent.summarize_context(_initial_description(), web_result="r")

    assert result.market_trends == "Trends"


def test_market_summarizer_agent_wraps_error(monkeypatch) -> None:
    prompt_loader = _prompt_loader()
    _patch_base_agent(monkeypatch, prompt_loader, raise_exc=RuntimeError("fail"))

    agent = MarketIntelligenceSummarizerAgent(prompt_loader)

    with pytest.raises(LLMParsingException):
        agent.summarize_context(_initial_description(), web_result="r")


def test_market_validator_agent_happy_path(monkeypatch) -> None:
    prompt_loader = _prompt_loader()
    parsed = _refined_context()
    _patch_base_agent(monkeypatch, prompt_loader, parsed=parsed)

    agent = MarketIntelligenceValidatorAgent(prompt_loader)
    result = agent.validate_context(_initial_description(), _market_context())

    assert result.is_valid is True


def test_market_validator_agent_wraps_error(monkeypatch) -> None:
    prompt_loader = _prompt_loader()
    _patch_base_agent(monkeypatch, prompt_loader, raise_exc=RuntimeError("fail"))

    agent = MarketIntelligenceValidatorAgent(prompt_loader)

    with pytest.raises(LLMParsingException):
        agent.validate_context(_initial_description(), _market_context())


def test_backlog_cleaner_agent_happy_path(monkeypatch) -> None:
    prompt_loader = _prompt_loader()
    parsed = _backlog_structure()
    _patch_base_agent(monkeypatch, prompt_loader, parsed=parsed)

    agent = BacklogCleanerAgent(prompt_loader)
    result = agent.clean_backlog(_backlog_structure())

    assert result.epics[0].epic.title == "Epic"


def test_backlog_cleaner_agent_wraps_error(monkeypatch) -> None:
    prompt_loader = _prompt_loader()
    _patch_base_agent(monkeypatch, prompt_loader, raise_exc=RuntimeError("fail"))

    agent = BacklogCleanerAgent(prompt_loader)

    with pytest.raises(LLMParsingException):
        agent.clean_backlog(_backlog_structure())


def test_backlog_prioritizer_agent_happy_path(monkeypatch) -> None:
    prompt_loader = _prompt_loader()
    parsed = _backlog_structure()
    _patch_base_agent(monkeypatch, prompt_loader, parsed=parsed)

    agent = BacklogPrioritizerAgent(prompt_loader)
    result = agent.prioritize(_backlog_structure())

    assert result.epics[0].epic.title == "Epic"


def test_backlog_prioritizer_agent_wraps_error(monkeypatch) -> None:
    prompt_loader = _prompt_loader()
    _patch_base_agent(monkeypatch, prompt_loader, raise_exc=RuntimeError("fail"))

    agent = BacklogPrioritizerAgent(prompt_loader)

    with pytest.raises(LLMParsingException):
        agent.prioritize(_backlog_structure())


def test_sprint_planner_agent_happy_path(monkeypatch) -> None:
    prompt_loader = _prompt_loader()
    parsed = SprintPlanning(sprints=[])
    _patch_base_agent(monkeypatch, prompt_loader, parsed=parsed)

    agent = SprintPlannerAgent(prompt_loader)
    result = agent.generate_sprints(_backlog_structure())

    assert result.sprints == []


def test_sprint_planner_agent_wraps_error(monkeypatch) -> None:
    prompt_loader = _prompt_loader()
    _patch_base_agent(monkeypatch, prompt_loader, raise_exc=RuntimeError("fail"))

    agent = SprintPlannerAgent(prompt_loader)

    with pytest.raises(LLMParsingException):
        agent.generate_sprints(_backlog_structure())


def test_user_backlog_fixer_agent_happy_path(monkeypatch) -> None:
    prompt_loader = _prompt_loader()
    parsed = _backlog_validation()
    _patch_base_agent(monkeypatch, prompt_loader, parsed=parsed)

    agent = UserBacklogFixerAgent(prompt_loader)
    result = agent.fix_user_backlog(_backlog_structure(), _backlog_structure())

    assert result.is_valid is True


def test_user_backlog_fixer_agent_wraps_error(monkeypatch) -> None:
    prompt_loader = _prompt_loader()
    _patch_base_agent(monkeypatch, prompt_loader, raise_exc=RuntimeError("fail"))

    agent = UserBacklogFixerAgent(prompt_loader)

    with pytest.raises(LLMParsingException):
        agent.fix_user_backlog(_backlog_structure(), _backlog_structure())


@pytest.mark.asyncio
async def test_backlog_generation_orchestrator_agent_happy_path() -> None:
    epic_generator = MagicMock()
    epic_generator.generate_epics.return_value = EpicList(
        epics=[Epic(title="Epic", description="Desc")]
    )
    user_story_generator = MagicMock()
    user_story_generator.generate_user_stories_by_epic.return_value = UserStoryList(
        epic_title="Epic",
        user_stories=[UserStory(title="Story", description="Desc")],
    )
    task_generator = MagicMock()
    task_generator.generate_tasks_by_user_story.return_value = TaskList(
        user_story_title="Story",
        tasks=[Task(title="Task", description="Desc")],
    )
    cleaner = MagicMock()
    cleaner.clean_backlog.return_value = _backlog_structure()

    agent = BacklogGenerationOrchestratorAgent(
        epic_generator=epic_generator,
        user_story_generator=user_story_generator,
        task_generator=task_generator,
        backlog_cleaner=cleaner,
    )

    result = await agent.generate(_initial_description(), _refined_context())

    assert result.epics[0].epic.title == "Epic"


@pytest.mark.asyncio
async def test_backlog_generation_orchestrator_agent_all_epics_fail() -> None:
    epic_generator = MagicMock()
    epic_generator.generate_epics.return_value = EpicList(
        epics=[Epic(title="Epic", description="Desc")]
    )
    user_story_generator = MagicMock()
    user_story_generator.generate_user_stories_by_epic.side_effect = RuntimeError("fail")
    task_generator = MagicMock()
    cleaner = MagicMock()

    agent = BacklogGenerationOrchestratorAgent(
        epic_generator=epic_generator,
        user_story_generator=user_story_generator,
        task_generator=task_generator,
        backlog_cleaner=cleaner,
    )

    cleaner.clean_backlog.return_value = MagicMock(name="cleaned_backlog")

    result = await agent.generate(_initial_description(), _refined_context())

    cleaner.clean_backlog.assert_called_once()
    assert result == cleaner.clean_backlog.return_value
