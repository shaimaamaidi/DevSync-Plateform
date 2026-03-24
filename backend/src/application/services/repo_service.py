from typing import List

from backend.src.domain.entities.git_repo import GitRepoDTO, GitRepoDetailDTO
from backend.src.domain.ports.repositories.i_repo_repository import IRepoRepository


class RepoService:
    def __init__(self, repo_repo: IRepoRepository):
        self._repo = repo_repo

    def add_repo(self, repo: GitRepoDTO) -> GitRepoDTO:
        return self._repo.save(repo)

    def update_repo(self, repo: GitRepoDTO) -> GitRepoDTO:
        return self._repo.update(repo)

    def get_by_id(self, repo_id: int) -> GitRepoDTO:
        return self._repo.find_by_id(repo_id)

    def get_by_name(self, name: str) -> GitRepoDTO:
        return self._repo.find_by_name(name)

    def get_by_url(self, url: str) -> GitRepoDTO:
        return self._repo.find_by_url(url)

    def get_all(self) -> List[GitRepoDTO]:
        return self._repo.find_all()

    def get_all_with_details(self) -> List[GitRepoDetailDTO]:
        return self._repo.find_all_with_details()

    def delete(self, repo_id: int) -> bool:
        return self._repo.delete(repo_id)