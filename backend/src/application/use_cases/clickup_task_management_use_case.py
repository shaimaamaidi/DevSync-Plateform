"""
ClickUp task creation and management use case module.

This module provides the ClickUpTaskCreationUseCase class, which is responsible
for handling task creation, update, and deletion operations in ClickUp.

It acts as an application-level use case that orchestrates domain entities
and delegates persistence and external API operations to ClickUpReader and
ClickUpTaskWriter ports.

Classes:
    ClickUpTaskCreationUseCase: Use case for managing ClickUp tasks.
"""

import logging

from backend.src.domain.entities.clickup.create_task_request import CreateTaskRequest
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.clickup.update_task_request import UpdateTaskRequest
from backend.src.domain.ports.input.i_clickup_task_management_use_case import IClickUpTaskManagementUseCase
from backend.src.domain.ports.output.clickup.i_clickup_reader import IClickUpReader
from backend.src.domain.ports.output.clickup.i_clickup_task_writer import IClickUpTaskWriter


logger = logging.getLogger(__name__)


class ClickUpTaskManagementUseCase(IClickUpTaskManagementUseCase):
    """
    Application use case for ClickUp task lifecycle management.

    This class is responsible for creating, updating, and deleting tasks
    in ClickUp. It orchestrates domain entities and interacts with external
    systems through reader and writer ports.

    Attributes:
        _clickup_reader (IClickUpReader): Port used to retrieve ClickUp data.
        _click_writer (IClickUpTaskWriter): Port used to write tasks to ClickUp.
    """

    def __init__(self, clickup_writer: IClickUpTaskWriter, clickup_reader: IClickUpReader):
        """
        Initialize the use case with required ClickUp ports.

        Args:
            clickup_writer (IClickUpTaskWriter): Writer port for task operations.
            clickup_reader (IClickUpReader): Reader port for fetching ClickUp data.
        """
        self._clickup_reader = clickup_reader
        self._click_writer = clickup_writer

    def create_task(self, request: CreateTaskRequest) -> ClickUpTask:
        """
        Create a new ClickUp task.

        Args:
            request (CreateTaskRequest): Task creation payload.

        Returns:
            ClickUpTask: The created ClickUp task entity containing task metadata returned by the ClickUp API.
        """
        logger.info(
            "Creating ClickUp task. list_id=%s space_id=%s name=%s",
            request.list_id,
            request.space_id,
            request.name,
        )

        task = ClickUpTask(
            id=None,
            name=request.name,
            description=request.description,
            status=request.status,
            priority=request.priority,
            assignee=request.assignees,
        )

        email_to_id = {}

        if request.assignees:
            members = self._clickup_reader.get_workspace_members()

            if members:
                email_to_id = {m["email"].lower(): m["id"] for m in members}

            logger.info(
                "Workspace members loaded for task creation. space_id=%s members=%d",
                request.space_id,
                len(email_to_id),
            )

        result = self._click_writer.create_task_by_list(
            request.list_id,
            task,
            email_to_id,
            request.ignore_mails,
        )

        logger.info(
            "Task created successfully. list_id=%s name=%s",
            request.list_id,
            request.name,
        )

        return result

    def update_task(self, request: UpdateTaskRequest) -> ClickUpTask:
        """
        Update an existing ClickUp task.

        Args:
            request (UpdateTaskRequest): Task update payload.

        Returns:
            ClickUpTask: The updated ClickUp task entity reflecting the latest state returned by
                the ClickUp API.
        """
        logger.info(
            "Updating ClickUp task. task_id=%s task_name=%s",
            request.task_id,
            request.name,
        )

        task = ClickUpTask(
            id=None,
            name=request.name,
            description=request.description,
            status=request.status,
            priority=request.priority,
            assignee=request.assignees,
        )

        email_to_id = {}

        if request.assignees or request.old_assignees:
            members = self._clickup_reader.get_workspace_members()

            if members:
                email_to_id = {m["email"].lower(): m["id"] for m in members}

            logger.info(
                "Workspace members loaded for task update. space_id=%s members=%d",
                request.space_id,
                len(email_to_id),
            )

        result = self._click_writer.update_task(
            request.task_id,
            task,
            request.old_assignees,
            email_to_id,
            request.ignore_mails,
        )

        logger.info(
            "Task updated successfully. list_id=%s name=%s",
            request.list_id,
            request.name,
        )

        return result

    def delete_task(self, task_id: str) -> bool:
        """
        Delete a ClickUp task.

        Args:
            task_id (str): Identifier of the task to delete.

        Returns:
            bool: True if the task was successfully deleted.
        """
        logger.info("Deleting ClickUp task. tas_id=%s", task_id)

        result = self._click_writer.delete_task(task_id)

        logger.info("Task deleted successfully. task_id=%s", task_id)

        return result