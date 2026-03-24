from typing import List

from backend.src.domain.entities.git_repo import GitRepoDTO, GitRepoDetailDTO
from backend.src.domain.exceptions.repo_not_found_exception import RepoNotFoundException
from backend.src.domain.ports.repositories.i_repo_repository import IRepoRepository


class RepoService:
    def __init__(self, repo_repo: IRepoRepository):
        self._repo = repo_repo

    def add_repo(self, name: str, url: str) -> GitRepoDTO:
        try:
            existing = self._repo.find_by_url(url)
            existing.name = name
            return self._repo.save(existing)
        except RepoNotFoundException:
            return self._repo.save(GitRepoDTO(name=name, url=url))

    def get_by_id(self, repo_id: int) -> GitRepoDTO:
        return self._repo.find_by_id(repo_id)

    def get_by_name(self, name: str) -> GitRepoDTO:
        return self._repo.find_by_name(name)

    def get_all(self) -> List[GitRepoDTO]:
        return self._repo.find_all()

    def get_all_with_details(self) -> List[GitRepoDetailDTO]:
        return self._repo.find_all_with_details()

    def update(self, repo_id: int, name: str = None, url: str = None) -> GitRepoDTO:
        dto = self._repo.find_by_id(repo_id)
        if name:
            dto.name = name
        if url:
            dto.url = url
        return self._repo.save(dto)

    def delete(self, repo_id: int) -> bool:
        return self._repo.delete(repo_id)