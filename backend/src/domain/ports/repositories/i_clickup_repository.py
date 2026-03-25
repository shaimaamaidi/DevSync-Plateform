from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.clickup_space import ClickUpSpaceDTO, ClickUpSpaceLightDTO


class IClickUpRepository(ABC):
    @abstractmethod
    def save(self, space: ClickUpSpaceDTO) -> ClickUpSpaceDTO:
        pass

    @abstractmethod
    def update(self, space: ClickUpSpaceDTO) -> ClickUpSpaceDTO:
        pass

    @abstractmethod
    def find_by_id(self, space_id: int) -> ClickUpSpaceDTO:
        pass

    @abstractmethod
    def find_by_space_code(self, space_id: str) -> ClickUpSpaceDTO:
        pass

    @abstractmethod
    def find_all(self) -> List[ClickUpSpaceDTO]:
        pass

    @abstractmethod
    def find_all_light(self) -> List[ClickUpSpaceLightDTO]:
        pass

    @abstractmethod
    def delete(self, space_id: int) -> bool:
        pass