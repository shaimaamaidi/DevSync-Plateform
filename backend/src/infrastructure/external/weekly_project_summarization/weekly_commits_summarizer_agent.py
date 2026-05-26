"""
Weekly commits summarizer agent.

This module defines the WeeklyCommitsSummarizerAgent, responsible for
analyzing weekly GitHub commit activity through an LLM.
It generates a concise narrative summary describing the
main development progress and technical work completed during the week.
"""

import logging
import json
from typing import List

from backend.src.domain.entities.github.commit import CommitDTO
from backend.src.domain.entities.weekly_project_summary.weekly_summary_narrative import WeeklySummaryNarrative
from backend.src.domain.ports.services.prompt_loading.i_prompt_loader import IPromptLoader
from backend.src.domain.ports.services.weekly_project_summarization.i_weekly_commits_summarizer import IWeeklyCommitsSummarizer
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent


logger = logging.getLogger(__name__)


class WeeklyCommitsSummarizerAgent(BaseAgent[WeeklySummaryNarrative], IWeeklyCommitsSummarizer):
    """
    LLM-based implementation of IWeeklyCommitsSummarizer.

    This agent is responsible for:
    - Analyzing weekly GitHub commit activity
    - Identifying key technical changes and development efforts
    - Summarizing implementation progress achieved during the week
    - Producing a concise and structured narrative overview

    The agent leverages an LLM to transform raw commit history
    into a human-readable weekly engineering summary.
    """

    def __init__(self, prompt_loader: IPromptLoader):
        """
        Initialize the WeeklyCommitsSummarizerAgent.

        Args:
            prompt_loader (IPromptLoader): Service responsible for loading
                prompt templates used by the agent during LLM interactions.
        """
        super().__init__(prompt_loader=prompt_loader)

    def summarize_commits(self, commits: List[CommitDTO]) -> str:
        """
        Generate a narrative summary of weekly GitHub commits using an LLM.

        This method:
        - Serializes commit history data
        - Sends the commit context to the LLM
        - Interprets the returned narrative summary

        The summarization process focuses on:
        - Main implementation work completed
        - Technical improvements and fixes
        - Development trends and progress
        - Overall engineering activity during the week

        Args:
            commits: List of GitHub commits to summarize.

        Returns:
            str: Human-readable weekly summary narrative describing
                the main development activities and accomplishments.

        Raises:
            LLMNetworkException: If a network error occurs while contacting the LLM.
            LLMApiException: If the LLM API returns an error response.
            LLMParsingException: If the LLM response cannot be parsed correctly.
        """
        logger.info("Summarize weekly commits process.")

        result: WeeklySummaryNarrative = self._call_llm(
            agent_name="WeeklyCommitsSummarizerAgent",
            folder_name="weekly_project_summarization",
            prompt_name="weekly_commits_summarizer_agent",
            variables={
                "commits": json.dumps(
                    [c.to_dict() for c in commits],
                    ensure_ascii=False,
                    default=str,
                    indent=2
                )
            },
            response_format=WeeklySummaryNarrative,
        )

        if not result or not result.summary:
            logger.warning("No summary result returned.")
            return ""

        logger.info("Weekly commits summary completed.")

        return result.summary