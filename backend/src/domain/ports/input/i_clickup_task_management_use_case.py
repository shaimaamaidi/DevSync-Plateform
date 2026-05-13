"""
Use case port for ClickUp task management operations.

This module defines the IClickUpTaskManagementUseCase interface, which specifies
operations for managing ClickUp tasks such as creation, update, and deletion.

It acts as a contract for application-level use cases responsible for:
- Creating tasks in ClickUp lists
- Updating existing tasks with new data
- Deleting tasks from ClickUp workspace

This abstraction isolates the domain/application layer from external ClickUp API
details and infrastructure-specific implementations.
"""

from abc import ABC, abstractmethod

from backend.src.domain.entities.clickup.create_task_request import CreateTaskRequest
from backend.src.domain.entities.clickup.update_task_request import UpdateTaskRequest


class IClickUpTaskManagementUseCase(ABC):
    """
    Define ClickUp task management behavior required by the application.

    This interface represents the contract for managing ClickUp tasks,
    abstracting external ClickUp API access and infrastructure concerns.

    It provides operations for:
    - Creating tasks in ClickUp
    - Updating existing tasks
    - Deleting tasks
    """

    @abstractmethod
    def create_task(self, request: CreateTaskRequest):
        """
        Create a new task in ClickUp.

        Args:
            request (CreateTaskRequest): Payload containing all required data
            to create a ClickUp task (title, description, list, assignees, etc.).

        Returns:
            Any: The created task response (typically task metadata or API response).
        """
        pass

    @abstractmethod
    def update_task(self, request: UpdateTaskRequest):
        """
        Update an existing ClickUp task.

        Args:
            request (UpdateTaskRequest): Payload containing task identifier
            and fields to update (name, status, description, assignees, etc.).

        Returns:
            Any: The updated task response from ClickUp.
        """
        pass

    @abstractmethod
    def delete_task(self, task_id: str):
        """
        Delete a ClickUp task.

        Args:
            task_id (str): Identifier of the task to delete.

        Returns:
            Any: Confirmation response from ClickUp after deletion.
        """
        pass