from typing import List

from backend.src.domain.entities.clickup_space import ClickUpSpaceDTO, ClickUpSpaceLightDTO
from backend.src.domain.ports.repositories.i_clickup_repository import IClickUpRepository


class ClickUpService:
    def __init__(self, clickup_repo: IClickUpRepository):
        self._repo = clickup_repo

    def add_space(self, space: ClickUpSpaceDTO) -> ClickUpSpaceDTO:
        return self._repo.save(space)

    def update_space(self, space: ClickUpSpaceDTO) -> ClickUpSpaceDTO:
        return self._repo.update(space)

    def get_by_id(self, space_id: int) -> ClickUpSpaceDTO:
        return self._repo.find_by_id(space_id)

    def get_by_space_id(self, space_id: str) -> ClickUpSpaceDTO:
        return self._repo.find_by_space_id(space_id)

    def get_all(self) -> List[ClickUpSpaceDTO]:
        return self._repo.find_all()

    def get_all_light(self) -> List[ClickUpSpaceLightDTO]:
        return self._repo.find_all_light()

    def delete(self, space_id: int) -> bool:
        return self._repo.delete(space_id)