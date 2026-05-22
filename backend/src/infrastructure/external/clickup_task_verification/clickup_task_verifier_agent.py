"""
ClickUp task verifier agent.

This module defines the ClickUpTaskVerifierAgent, responsible for verifying
generated ClickUp tasks against existing tasks using an LLM. It ensures that
only relevant create or update actions are produced based on differences
between generated and existing tasks.
"""

import logging
import json
from typing import List

from openai import APIConnectionError, APIStatusError
from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionSystemMessageParam

from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.generated_tasks.generated_task_from_summary import GeneratedTaskFromSummary
from backend.src.domain.entities.verify_tasks.verified_task import VerifiedTask, VerifiedTaskList
from backend.src.domain.exceptions.llm.llm_api_exception import LLMApiException
from backend.src.domain.exceptions.llm.llm_network_exception import LLMNetworkException
from backend.src.domain.exceptions.llm.llm_parsing_exception import LLMParsingException
from backend.src.domain.ports.services.clickup_task_verification.i_clickup_task_verifier import IClickUpTaskVerifier
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent


logger = logging.getLogger(__name__)


class ClickUpTaskVerifierAgent(BaseAgent, IClickUpTaskVerifier):
    """
    LLM-based implementation of IClickUpTaskVerifier.

    This agent is responsible for:
    - Comparing generated tasks with existing ClickUp tasks
    - Identifying tasks to create or update
    - Filtering out redundant updates with no effective changes
    """

    def verify_tasks(
        self,
        existing_tasks: List[ClickUpTask],
        tasks: List[GeneratedTaskFromSummary],
    ) -> List[VerifiedTask]:
        """
        Verify generated ClickUp tasks against existing tasks using an LLM.

        This method:
        - Sends existing and generated tasks to the LLM
        - Uses prompt templates to guide verification and action detection
        - Parses the LLM response into verification results
        - Filters out updates that do not introduce real changes

        Args:
            existing_tasks(List[ClickUpTask]): Tasks already present in ClickUp.
            tasks(List[GeneratedTaskFromSummary]): Tasks produced by the LLM.

        Returns:
            List[VerifiedTask]: List of tasks requiring creation or update.

        Raises:
            LLMNetworkException: If a network error occurs while contacting the LLM.
            LLMApiException: If the LLM API returns an error response.
            LLMParsingException: If the LLM response cannot be parsed correctly.
        """
        logger.info(
            "Starting verification: %d generated task(s) against %d existing task(s).",
            len(tasks),
            len(existing_tasks),
        )

        if not tasks:
            logger.warning("No tasks to verify — skipping verification.")
            return []

        messages = self.prompt_loader.get_messages(
            folder_name="task_verification",
            name="task_verifier_agent",
            variables={
                "existing_tasks": self._serialize_existing(existing_tasks),
                "generated_tasks": self._serialize_generated(tasks)
            }
        )

        messages = [
            ChatCompletionSystemMessageParam(role="system", content=messages["system"]),
            ChatCompletionUserMessageParam(role="user", content=messages["user"])
        ]

        try:
            response = self.client.chat.completions.parse(
                model=self.model,
                messages=messages,
                temperature=0,
                response_format=VerifiedTaskList,
            )
        except APIConnectionError as e:
            logger.exception("Network error contacting LLM in ClickUpTaskVerifierAgent: reason=%s.", str(e))
            raise LLMNetworkException() from e

        except APIStatusError as e:
            logger.exception("LLM API error in ClickUpTaskVerifierAgent: status=%d.", e.status_code)
            raise LLMApiException() from e

        except Exception as e:
            logger.exception("Click up tasks verifying failed: reason=%s.", str(e))
            raise LLMParsingException() from e

        parsed: VerifiedTaskList = response.choices[0].message.parsed
        if not parsed or not parsed.results:
            logger.warning("No tasks extracted from meeting summary.")
            return []

        logger.info(
            "Verification response received. results=%d.",
            len(parsed.results) if parsed.results else 0,
        )

        filtered = ClickUpTaskVerifierAgent._filter_unchanged_updates(parsed.results, existing_tasks)

        logger.info(
            "Verification complete: %d action(s) to apply (%d create, %d update).",
            len(filtered),
            sum(1 for r in filtered if r.action == "create"),
            sum(1 for r in filtered if r.action == "update"),
        )
        return filtered

    @staticmethod
    def _serialize_existing(tasks: List[ClickUpTask]) -> str:
        """
        Convert existing ClickUp tasks into a JSON string.

        This method prepares task data to be consumed by the LLM by
        transforming domain entities into a structured JSON format.

        Args:
            tasks: List of existing ClickUp tasks.

        Returns:
            str: JSON representation of existing tasks.
        """
        return json.dumps(
            [
                {
                    "id": t.id,
                    "name": t.name,
                    "description": t.description,
                    "status": t.status,
                    "priority": t.priority,
                    "assignee": t.assignee,
                }
                for t in tasks
            ],
            ensure_ascii=False,
            indent=2,
        )

    @staticmethod
    def _serialize_generated(tasks: List[GeneratedTaskFromSummary]) -> str:
        """
        Convert generated tasks into a JSON string.

        This method prepares LLM-generated tasks for verification by
        formatting them into a structured JSON representation.

        Args:
            tasks: List of generated tasks.

        Returns:
            str: JSON representation of generated tasks.
        """
        return json.dumps(
            [
                {
                    "task_name": t.task_name,
                    "task_description": t.task_description,
                    "task_status": t.task_status,
                    "task_priority": t.task_priority,
                    "task_assigne": t.task_assigne,
                    "location": t.location,
                }
                for t in tasks
            ],
            ensure_ascii=False,
            indent=2,
        )

    @staticmethod
    def _filter_unchanged_updates(
        results: List[VerifiedTask],
        existing_tasks: List[ClickUpTask],
    ) -> List[VerifiedTask]:
        """
        Filter out update actions that do not introduce any real changes.

        This method ensures that redundant updates (i.e., updates where
        no meaningful field has changed) are excluded from the final result.

        Args:
            results: Verification results returned by the LLM.
            existing_tasks: List of existing ClickUp tasks.

        Returns:
            List[VerifiedTask]: Filtered list of actionable tasks.
        """
        existing_map = {t.id: t for t in existing_tasks}
        filtered = []

        for result in results:
            if ClickUpTaskVerifierAgent._is_redundant_update(result, existing_map):
                logger.warning(
                    "No real change detected for task '%s' (id='%s') — skipping.",
                    result.task_name,
                    result.task_id,
                )
                continue
            filtered.append(result)
        return filtered

    @staticmethod
    def _is_redundant_update(
        result: VerifiedTask,
        existing_map: dict,
    ) -> bool:
        """
        Determine whether an update action contains no effective changes.

        Args:
            result: Verification result for a task.
            existing_map: Mapping of task IDs to existing tasks.

        Returns:
            bool: True if the update is redundant, False otherwise.
        """
        if result.action != "update" or not result.task_id:
            return False

        existing = existing_map.get(result.task_id)
        if not existing:
            return False

        return not any([
            ClickUpTaskVerifierAgent._status_changed(result, existing),
            ClickUpTaskVerifierAgent._priority_changed(result, existing),
            ClickUpTaskVerifierAgent._assignee_changed(result, existing),
        ])

    @staticmethod
    def _status_changed(result: VerifiedTask, existing: ClickUpTask) -> bool:
        """
        Check whether the task status has changed.

        Args:
            result: Verification result.
            existing: Existing ClickUp task.

        Returns:
            bool: True if status has changed, False otherwise.
        """
        return result.task_status != existing.status

    @staticmethod
    def _priority_changed(result: VerifiedTask, existing: ClickUpTask) -> bool:
        """
        Check whether the task priority has changed.

        Args:
            result: Verification result.
            existing: Existing ClickUp task.

        Returns:
            bool: True if priority has changed, False otherwise.
        """
        return result.task_priority != existing.priority

    @staticmethod
    def _assignee_changed(result: VerifiedTask, existing: ClickUpTask) -> bool:
        """
        Check whether the task assignees have changed.

        This method compares normalized assignee lists while ignoring
        empty values and undefined placeholders.

        Args:
            result: Verification result.
            existing: Existing ClickUp task.

        Returns:
            bool: True if assignees have changed, False otherwise.
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