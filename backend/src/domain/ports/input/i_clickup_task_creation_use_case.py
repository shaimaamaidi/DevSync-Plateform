from abc import ABC, abstractmethod

from backend.src.domain.entities.clickup.create_task_request import CreateTaskRequest
from backend.src.domain.entities.clickup.update_task_request import UpdateTaskRequest


class IClickUpTaskCreationUseCase(ABC):

    @abstractmethod
    def create_task(self, request: CreateTaskRequest):
        pass

    @abstractmethod
    def update_task(self, request: UpdateTaskRequest):
        pass

    @abstractmethod
    def delete_task(self, task_id: str):
        pass