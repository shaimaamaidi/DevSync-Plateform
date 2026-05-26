"""
Service port for commit-to-task mapping via LLMs.

This module defines the ICommitTaskMapper interface, which specifies
operations for mapping GitHub commits to their corresponding ClickUp tasks
using semantic analysis and LLM-based reasoning.

It enables traceability between development activity and task management
by identifying which task a given commit is related to.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask


class ICommitTaskMapper(ABC):
    """
    Define commit-to-task mapping behavior required by the application.

    This interface represents the contract for associating GitHub commits
    with ClickUp tasks based on semantic similarity and contextual analysis.
    """

    @abstractmethod
    def map_commit_task(
        self,
        commit: str,
        tasks: List[ClickUpTask],
    ) -> Optional[ClickUpTask]:
        """
        Map a GitHub commit to its corresponding ClickUp task.

        Args:
            commit: The GitHub commit message or identifier to analyze.
            tasks: List of ClickUp tasks to compare against.

        Returns:
            Optional[ClickUpTask]: The matched task if found, otherwise None.
        """
        pass