"""
Service port for summarizing weekly commits.

This module defines the IWeeklyCommitsSummarizer interface, which specifies
operations for generating a narrative summary from weekly GitHub commit activity.
"""

from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.github.commit import CommitDTO


class IWeeklyCommitsSummarizer(ABC):
    """
    Define weekly commits summarization behavior required by the application.

    This interface represents the contract for analyzing GitHub commit
    activity and generating a human-readable weekly development summary.
    """

    @abstractmethod
    def summarize_commits(self, commits: List[CommitDTO]) -> str:
        """
        Generate a narrative summary from weekly GitHub commits.

        Args:
            commits: List of GitHub commits to summarize.

        Returns:
            str: Human-readable summary describing the main
                development activities and technical progress.
        """
        pass