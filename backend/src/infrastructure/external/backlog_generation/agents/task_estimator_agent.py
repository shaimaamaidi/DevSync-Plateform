"""
Task estimator agent.

This module defines the TaskEstimatorAgent, responsible for estimating
effort for user stories inside an epic using an LLM.

The agent enriches each user story with a sprint-ready estimation by
leveraging epic-level context, product constraints, and planning inputs.
It ensures consistent, realistic, and comparable estimations across
all user stories within the same epic, supporting sprint planning
and workload distribution.
"""

import logging
from typing import List

from backend.src.domain.entities.backlog.structure import EpicBacklog
from backend.src.domain.entities.sprint.sprint import UserStorySprint, UserStoriesList
from backend.src.domain.ports.services.backlog_generation.agents.i_task_estimator import ITaskEstimator
from backend.src.domain.ports.services.prompt_loading.i_prompt_loader import IPromptLoader
from backend.src.infrastructure.external.backlog_generation.helpers.backlog_formatter import format_epic
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent


logger = logging.getLogger(__name__)


class TaskEstimatorAgent(BaseAgent[UserStoriesList], ITaskEstimator):
    """
    LLM-based implementation of ITaskEstimator.

    This agent is responsible for:
    - Estimating effort for user stories within an epic
    - Producing structured sprint-ready user stories with estimations
    - Using epic context to improve consistency and realism of estimates
    - Supporting sprint planning and workload distribution

    The estimation is performed using prompt-based LLM reasoning,
    ensuring coherence across all user stories in the same epic.
    """

    def __init__(self, prompt_loader: IPromptLoader):
        """
        Initialize the TaskEstimatorAgent.

        This constructor injects the prompt loader used to retrieve
        LLM templates for effort estimation.

        The prompt loader is responsible for:
        - Loading estimation prompts
        - Providing structured templates for sprint estimation
        - Ensuring consistent effort evaluation across user stories

        Args:
            prompt_loader (IPromptLoader): Service responsible for loading
                prompt templates used by the agent during LLM interactions.
        """
        super().__init__(prompt_loader)

    def estimate_tasks(self, context:str, epic: EpicBacklog) -> List[UserStorySprint]:
        """
        Estimate effort for all user stories inside an epic.

        This method uses an LLM to transform raw epic user stories into
        sprint-ready user stories enriched with effort estimation.
        The estimation takes into account:
        - Epic-level context
        - Business and functional coherence
        - Sprint planning constraints (when provided in context)

        Args:
            context (str): Additional planning or product context used for estimation.
            epic (EpicBacklog): The epic containing user stories to estimate.

        Returns:
            List[UserStorySprint]: List of user stories enriched with estimation data.

        Raises:
            LLMNetworkException: If a network error occurs while contacting the LLM.
            LLMApiException: If the LLM API returns an error response.
            LLMParsingException: If the response cannot be parsed into UserStoriesList.
        """
        logger.info("Starting task estimation generation.")

        result = self._call_llm(
            agent_name="TaskEstimatorAgent",
            folder_name="backlog_generation",
            prompt_name="task_estimator_agent",
            variables={
                "context": context,
                "epic": format_epic(epic)
            },
            response_format=UserStoriesList,
        )

        logger.info("Task estimation generation completed successfully.")

        return result.user_stories
