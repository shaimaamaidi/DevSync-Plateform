from typing import List

from backend.src.domain.entities.clickup_space import ClickUpSpaceDTO, ClickUpSpaceLightDTO
from backend.src.domain.entities.git_repo import GitRepoDTO
from backend.src.domain.exceptions.clickup_space_not_found_exception import ClickUpSpaceNotFoundException
from backend.src.domain.ports.repositories.i_clickup_repository import IClickUpRepository


class ClickUpService:
    def __init__(self, clickup_repo: IClickUpRepository):
        self._repo = clickup_repo

    def add_space(self, name: str, space_id: str, repo: GitRepoDTO = None) -> ClickUpSpaceDTO:
        try:
            existing = self._repo.find_by_space_id(space_id)
            existing.name = name
            if repo:
                existing.repo_id = repo.id
            return self._repo.save(existing)
        except ClickUpSpaceNotFoundException:
            repo_id = repo.id if repo else None
            return self._repo.save(ClickUpSpaceDTO(name=name, space_id=space_id, repo_id=repo_id))

    def get_by_id(self, space_id: int) -> ClickUpSpaceDTO:
        return self._repo.find_by_id(space_id)

    def get_all(self) -> List[ClickUpSpaceDTO]:
        return self._repo.find_all()

    def get_all_light(self) -> List[ClickUpSpaceLightDTO]:
        return self._repo.find_all_light()

    def update(self, space_id: int, name: str = None) -> ClickUpSpaceDTO:
        dto = self._repo.find_by_id(space_id)
        if name:
            dto.name = name
        return self._repo.save(dto)

    def delete(self, space_id: int) -> bool:
        return self._repo.delete(space_id)