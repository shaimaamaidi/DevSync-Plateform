from typing import List, Optional

from src.domain.entities.git_repo import GitRepoDTO, GitRepoDetailDTO
from src.domain.ports.repositories.i_repo_repository import IRepoRepository


class RepoService:
    def __init__(self, repo_repo: IRepoRepository):
        self._repo = repo_repo

    def add_repo(self, name: str, url: str) -> GitRepoDTO:
        existing = self._repo.find_by_url(url)
        if existing:
            existing.name = name
            return self._repo.save(existing)
        return self._repo.save(GitRepoDTO(name=name, url=url))

    def get_by_id(self, repo_id: int) -> Optional[GitRepoDTO]:
        return self._repo.find_by_id(repo_id)

    def get_by_name(self, name: str) -> Optional[GitRepoDTO]:
        return self._repo.find_by_name(name)

    def get_all(self) -> List[GitRepoDTO]:
        return self._repo.find_all()

    def get_all_with_details(self) -> List[GitRepoDetailDTO]:
        return self._repo.find_all_with_details()

    def update(self, repo_id: int, name: str = None, url: str = None) -> Optional[GitRepoDTO]:
        dto = self._repo.find_by_id(repo_id)
        if not dto:
            return None
        if name:
            dto.name = name
        if url:
            dto.url = url
        return self._repo.save(dto)

    def delete(self, repo_id: int) -> bool:
        return self._repo.delete(repo_id)