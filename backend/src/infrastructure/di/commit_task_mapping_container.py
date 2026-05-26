"""
Dependency container for commit-to-task mapping workflow.

This module defines the CommitTaskMappingContainer class, which wires together
AI agents, ClickUp infrastructure, and application use cases required for
mapping GitHub commits to ClickUp tasks.

It is responsible for initializing all components required for:
- Retrieval of ClickUp space structure
- Semantic mapping between commits and ClickUp tasks using LLM agents
- Integration between ClickUp and AI prompt services
- Orchestration of commit-to-task traceability workflows

Classes:
    CommitTaskMappingContainer: Application-scoped dependency injection container.
"""

import logging

from backend.src.application.use_cases.map_commit_task_use_case import MapCommitTaskUseCase

from backend.src.domain.exceptions.base.app_exception import AppException
from backend.src.infrastructure.di.bas_ai_container import BaseAIContainer

from backend.src.infrastructure.di.base_clickup_container import BaseClickUpContainer
from backend.src.infrastructure.external.commit_task_mapping.commit_task_mapper_agent import CommitTaskMapperAgent


logger = logging.getLogger(__name__)


class CommitTaskMappingContainer(BaseAIContainer, BaseClickUpContainer):
    """
    Dependency injection container for commit-to-task mapping workflow.

    This container orchestrates all dependencies required for mapping GitHub
    commits to ClickUp tasks.

    It is responsible for:
    - Initializing AI prompt-based agents for commit-task mapping
    - Initializing ClickUp infrastructure (via base container)
    - Wiring application use cases for commit-to-task mapping
    - Providing fully configured use cases for execution layer

    Attributes:
        commit_task_mapper_agent (CommitTaskMapperAgent):
            LLM-based agent responsible for semantic commit-to-task matching.

        commit_task_mapping_use_case (MapCommitTaskUseCase):
            Application use case responsible for orchestrating mapping workflow.
    """

    def __init__(self):
        """
        Initialize the CommitTaskMappingContainer.

        This constructor initializes all required infrastructure and agents:
        - AI prompt system (BaseAIContainer)
        - ClickUp infrastructure (BaseClickUpContainer)
        - Commit-task mapping LLM agent
        - Commit-task mapping application use case

        Raises:
            AppException: If any dependency initialization fails.
        """
        logger.info("Initializing commit task mapping container.")

        try:
            BaseAIContainer.__init__(self)
            BaseClickUpContainer.__init__(self)
            self._init_commit_task_mapper_agent()
            self._init_commit_task_mapping_use_cases()

            logger.info("Commit task mapping container initialized successfully.")

        except AppException:
            raise
        except Exception as e:
            logger.exception("Failed to initialize commit task mapping container.")
            raise AppException(
                "Commit task mapping service are currently unavailable. Please try again later.",
                "PROJECT_STATUS_CONTAINER_INIT_ERROR",
                http_status=500,
            ) from e

    def _init_commit_task_mapper_agent(self):
        """
        Initialize LLM-based commit task mapper agent.

        This agent is responsible for:
        - Analyzing GitHub commit messages
        - Comparing them with ClickUp tasks
        - Determining the most relevant task using semantic reasoning
        """
        logger.info("Initializing commit task mapper agent.")

        self.commit_task_mapper_agent = CommitTaskMapperAgent(self.prompt_loader)

    def _init_commit_task_mapping_use_cases(self):
        """
        Initialize commit-to-task mapping use cases.

        This method wires together:
        - ClickUp infrastructure (reader)
        - Commit-task mapper agent (LLM-based)

        into a fully functional application use case.
        """
        logger.info("Initializing commit task mapping use cases.")

        self.commit_task_mapping_use_case = MapCommitTaskUseCase(
            self.clickup_reader,
            self.commit_task_mapper_agent
        )

