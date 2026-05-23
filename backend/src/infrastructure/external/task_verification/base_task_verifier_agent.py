"""
Base task verifier agent.

This module defines the BaseTaskVerifierAgent, an abstract generic base class
for all LLM-based task verification agents. It centralizes shared verification
logic and delegates context-specific behavior to subclasses.
"""

import logging
import json
from abc import abstractmethod, ABC
from typing import List, Generic, TypeVar

from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.ports.services.iprompt_loader import IPromptLoader
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent


logger = logging.getLogger(__name__)


G = TypeVar("G")  # Generated task type to verify
V = TypeVar("V")  # Verified task type (result)
W = TypeVar("W")  # wrapper type ex: VerifiedTaskListFromSummary


class BaseTaskVerifierAgent(BaseAgent[W], Generic[G, V, W], ABC):
    """
    Abstract base class for all LLM-based task verifier agents.

    This class centralizes the shared verification workflow used to compare
    generated tasks against existing ClickUp tasks. It handles task
    verification orchestration, redundant update filtering, and common
    field comparison helpers while delegating context-specific behavior
    to subclasses.

    Subclasses are responsible for:
    - Defining prompt configuration
    - Providing response parsing format
    - Serializing generated tasks
    - Determining whether a task update contains effective changes

    Attributes:
        agent_name (str): Logical agent name used for logging and tracing.
        folder_name (str): Prompt folder name.
        prompt_name (str): Prompt template name.
        response_format: Structured response model used for LLM parsing.
    """
    def __init__(
        self,
        prompt_loader: IPromptLoader,
        agent_name: str,
        folder_name: str,
        prompt_name: str,
        response_format: type[W],
    ):
        super().__init__(prompt_loader)
        self.agent_name = agent_name
        self.folder_name = folder_name
        self.prompt_name = prompt_name
        self.response_format = response_format

    @abstractmethod
    def _serialize_generated(self, tasks: List[G]) -> str:
        """
        Serialize generated tasks into a format suitable for LLM verification.

        Subclasses must implement this method to transform generated tasks
        into a structured string representation that can be injected into
        the verification prompt.

        Args:
            tasks: Generated tasks to serialize.

        Returns:
            Structured serialized representation of generated tasks.
        """
        pass

    @abstractmethod
    def _has_effective_changes(self, result: V, existing: ClickUpTask) -> bool:
        """
        Determine whether a verified update contains effective changes.

        Subclasses must implement the comparison logic used to detect
        meaningful differences between a verified task result and an
        existing ClickUp task.

        Args:
            result: Verified task result returned by the LLM.
            existing: Existing ClickUp task.

        Returns:
            True if the update introduces meaningful changes, otherwise False.
        """
        pass

    def verify_tasks(self, existing_tasks: List[ClickUpTask], tasks: List[G]) -> List[V]:
        """
        Verify generated tasks against existing ClickUp tasks using the LLM.

        This method:
        - Serializes existing and generated tasks
        - Executes the verification prompt
        - Parses the structured LLM response
        - Filters redundant updates with no effective changes

        Args:
            existing_tasks: Existing ClickUp tasks already present in the list.
            tasks: Generated tasks to verify.

        Returns:
            List of verified task actions to apply.

        Raises:
            LLMNetworkException: If a network error occurs while contacting the LLM.
            LLMApiException: If the LLM API returns an error response.
            LLMParsingException: If the LLM response cannot be parsed correctly.
        """
        logger.info(
            "Starting verification: %d generated task(s) against %d existing task(s).",
            len(tasks), len(existing_tasks),
        )

        if not tasks:
            logger.warning("No tasks to verify — skipping verification.")
            return []

        serialized_tasks = json.dumps(
            [t.to_dict() for t in existing_tasks],
            ensure_ascii=False, indent=2,
        )

        parsed = self._call_llm(
            agent_name=self.agent_name,
            folder_name=self.folder_name,
            prompt_name=self.prompt_name,
            variables={
                "existing_tasks": serialized_tasks,
                "generated_tasks": self._serialize_generated(tasks),
            },
            response_format=self.response_format,
        )

        if not parsed or not parsed.results:
            logger.warning("No tasks extracted.")
            return []

        logger.info("Verification response received. results=%d.", len(parsed.results))

        filtered = self._filter_unchanged_updates(parsed.results, existing_tasks)

        logger.info(
            "Verification complete: %d action(s) to apply (%d create, %d update).",
            len(filtered),
            sum(1 for r in filtered if r.action == "create"),
            sum(1 for r in filtered if r.action == "update"),
        )
        return filtered

    def _filter_unchanged_updates(self, results: List[V], existing_tasks: List[ClickUpTask]) -> List[V]:
        """
        Remove update actions that do not introduce effective changes.

        Args:
            results: Verification results returned by the LLM.
            existing_tasks: Existing ClickUp tasks indexed for comparison.

        Returns:
           Filtered verification results containing only meaningful actions.
       """
        existing_map = {t.id: t for t in existing_tasks}
        filtered = []
        for result in results:
            if self._is_redundant_update(result, existing_map):
                logger.warning(
                    "No real change detected for task '%s' (id='%s') — skipping.",
                    result.task_name, result.task_id,
                )
                continue
            filtered.append(result)
        return filtered

    def _is_redundant_update(self, result: V, existing_map: dict) -> bool:
        """
        Determine whether an update action is redundant.

        An update is considered redundant when the target task already
        contains the same effective values.

        Args:
            result: Verified task action.
            existing_map: Mapping of existing tasks indexed by task ID.

        Returns:
            True if the update introduces no effective changes, otherwise False.
        """
        if result.action != "update" or not result.task_id:
            return False
        existing = existing_map.get(result.task_id)
        if not existing:
            return False
        return not self._has_effective_changes(result, existing)

    @staticmethod
    def _status_changed(result, existing: ClickUpTask) -> bool:
        """
        Check whether the task status has changed.
        """
        return result.task_status != existing.status

    @staticmethod
    def _priority_changed(result, existing: ClickUpTask) -> bool:
        """
        Check whether the task priority has changed.
        """
        return result.task_priority != existing.priority

    @staticmethod
    def _assignee_changed(result, existing: ClickUpTask) -> bool:
        """
        Check whether the task assignees have changed.
        """
        new_assignees = {
            a.strip()
            for a in result.task_assigne.split(",")
            if a.strip() and a.strip() != "غير محدد"
        }
        existing_assignees = {
            a.strip()
            for a in (existing.assignee or "").split(",")
            if a.strip()
        }
        return bool(new_assignees - existing_assignees)