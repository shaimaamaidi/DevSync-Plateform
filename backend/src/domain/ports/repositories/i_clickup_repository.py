from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.clickup_space import (
    ClickUpSpaceCreateDTO,
    ClickUpSpaceDTO,
    ClickUpSpaceDetailDTO,
    ClickUpSpaceLightDTO,
    ClickUpSpaceUpdateDTO,
)


class IClickUpRepository(ABC):
    @abstractmethod
    def save(self, space: ClickUpSpaceCreateDTO) -> ClickUpSpaceDTO:
        pass

    @abstractmethod
    def update(self, space: ClickUpSpaceUpdateDTO) -> ClickUpSpaceDetailDTO:
        pass

    @abstractmethod
    def find_by_id(self, space_id: int) -> ClickUpSpaceDetailDTO:
        pass

    @abstractmethod
    def find_by_space_code(self, space_code: str) -> ClickUpSpaceDTO:
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