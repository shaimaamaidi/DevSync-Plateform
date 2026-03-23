from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.clickup_space import ClickUpSpaceDTO, ClickUpSpaceLightDTO


class IClickUpRepository(ABC):
    @abstractmethod
    def save(self, space: ClickUpSpaceDTO) -> ClickUpSpaceDTO:
        pass

    @abstractmethod
    def find_by_id(self, space_id: int) -> Optional[ClickUpSpaceDTO]:
        pass

    @abstractmethod
    def find_by_space_id(self, space_id: str) -> Optional[ClickUpSpaceDTO]:
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