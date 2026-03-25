from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.git_repo import GitRepoDTO, GitRepoDetailDTO

class IRepoRepository(ABC):
    @abstractmethod
    def save(self, repo: GitRepoDTO) -> GitRepoDetailDTO:
        pass

    @abstractmethod
    def update(self, repo: GitRepoDetailDTO) -> GitRepoDetailDTO:
        pass

    @abstractmethod
    def find_by_id(self, repo_id: int) -> GitRepoDetailDTO:
        pass

    @abstractmethod
    def find_by_url(self, url: str) -> GitRepoDetailDTO:
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> GitRepoDetailDTO:
        pass

    @abstractmethod
    def find_all_with_details(self) -> List[GitRepoDetailDTO]:
        pass

    @abstractmethod
    def delete(self, repo_id: int) -> bool:
        pass
