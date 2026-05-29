"""
Use case port for task search operations.

This module defines the ISearchTaskUseCase interface, which specifies
operations for searching ClickUp tasks within a given space based on
a natural language question.

It acts as the application layer orchestration contract for:
- Interpreting user search queries
- Delegating task search to domain/LLM agents
- Returning structured user-facing search responses
"""

from abc import ABC, abstractmethod

from backend.src.domain.entities.checked_task_status.task_search_response import (
    TaskSearchResponse,
)


class ISearchTaskUseCase(ABC):
    """
    Define task search use case behavior required by the application.

    This interface represents the contract for searching ClickUp tasks
    inside a specific space using a natural language question. It abstracts
    the orchestration between domain services, LLM agents, and response
    formatting logic.
    """

    @abstractmethod
    def search_task(self, description: str, space_id: str) -> TaskSearchResponse:
        """
        Search ClickUp tasks based on a user question and space identifier.

        Args:
            description: Natural language phrase describing what tasks to find.
            space_id: Identifier of the ClickUp space to search within.

        Returns:
            TaskSearchResponse: Structured response containing a user-facing
                message and matching ClickUp tasks.
        """
        pass