"""
Weekly deployments summarizer agent.

This module defines the WeeklyDeploymentsSummarizerAgent, responsible for
analyzing weekly deployment activity through an LLM.
It generates a concise narrative summary describing deployment progress,
release activity, and delivery outcomes during the week.
"""

import logging
from typing import List

from backend.src.domain.entities.github.deployment import DeploymentDTO
from backend.src.domain.entities.weekly_project_summary.weekly_summary_narrative import WeeklySummaryNarrative
from backend.src.domain.ports.services.prompt_loading.i_prompt_loader import IPromptLoader
from backend.src.domain.ports.services.weekly_project_summarization.i_weekly_deployments_summarizer import IWeeklyDeploymentsSummarizer
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent


logger = logging.getLogger(__name__)


class WeeklyDeploymentsSummarizerAgent(BaseAgent[WeeklySummaryNarrative], IWeeklyDeploymentsSummarizer):
    """
    LLM-based implementation of IWeeklyDeploymentsSummarizer.

    This agent is responsible for:
    - Analyzing weekly deployment activity
    - Identifying delivered releases and environments impacted
    - Summarizing deployment progress and operational outcomes
    - Producing a concise and structured deployment narrative

    The agent leverages an LLM to transform raw deployment history
    into a human-readable weekly delivery summary.
    """

    def __init__(self, prompt_loader: IPromptLoader):
        """
        Initialize the WeeklyDeploymentsSummarizerAgent.

        Args:
            prompt_loader (IPromptLoader): Service responsible for loading
                prompt templates used by the agent during LLM interactions.
        """
        super().__init__(prompt_loader=prompt_loader)

    def summarize_deployments(self, deployments: List[DeploymentDTO]) -> str:
        """
        Generate a narrative summary of weekly deployments using an LLM.

        This method:
        - Serializes deployment history data
        - Sends the deployment context to the LLM
        - Interprets the returned narrative summary

        The summarization process focuses on:
        - Deployment and release activity
        - Delivery progress across environments
        - Operational and production updates
        - Overall release cadence during the week

        Args:
            deployments: List of deployments to summarize.

        Returns:
            str: Human-readable weekly deployment summary describing
                the main release and delivery activities.

        Raises:
            LLMNetworkException: If a network error occurs while contacting the LLM.
            LLMApiException: If the LLM API returns an error response.
            LLMParsingException: If the LLM response cannot be parsed correctly.
        """
        logger.info("Summarize weekly deployments process.")

        if not deployments:
            return "No deployments were recorded this week."

        sorted_deployments = sorted(deployments, key=lambda d: d.created_at, reverse=True)

        result: WeeklySummaryNarrative = self._call_llm(
            agent_name="WeeklyDeploymentsSummarizerAgent",
            folder_name="weekly_project_summarization",
            prompt_name="weekly_deployments_summarizer_agent",
            variables={
                "deployments": [{
                        "environment": d.environment,
                        "ref": d.ref,
                        "creator": d.creator,
                        "created_at": d.created_at.isoformat(),
                        "state": d.state,
                    }
                    for d in sorted_deployments
                ],
                "total_count": len(sorted_deployments)
            },
            response_format=WeeklySummaryNarrative,
        )

        if not result or not result.summary:
            logger.warning("No summary result returned.")
            return "No deployments were recorded this week."

        logger.info("Weekly deployments summary completed.")

        return result.summary