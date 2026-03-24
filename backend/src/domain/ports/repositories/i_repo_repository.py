from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.git_repo import GitRepoDTO, GitRepoDetailDTO

class IRepoRepository(ABC):
    @abstractmethod
    def save(self, repo: GitRepoDTO) -> GitRepoDTO:
        pass

    @abstractmethod
    def find_by_id(self, repo_id: int) -> GitRepoDTO:
        pass

    @abstractmethod
    def find_by_url(self, url: str) -> GitRepoDTO:
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> GitRepoDTO:
        pass

    @abstractmethod
    def find_all(self) -> List[GitRepoDTO]:
        pass

    @abstractmethod
    def find_all_with_details(self) -> List[GitRepoDetailDTO]:
        pass

    @abstractmethod
    def delete(self, repo_id: int) -> bool:
        pass
