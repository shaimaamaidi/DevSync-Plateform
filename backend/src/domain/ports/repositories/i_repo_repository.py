from abc import ABC, abstractmethod
from typing import List, Optional

from backend.src.domain.entities.git_repo import GitRepoDTO, GitRepoDetailDTO

class IRepoRepository(ABC):
    @abstractmethod
    def save(self, repo: GitRepoDTO) -> GitRepoDTO:
        pass

    @abstractmethod
    def find_by_id(self, repo_id: int) -> Optional[GitRepoDTO]:
        pass

    @abstractmethod
    def find_by_url(self, url: str) -> Optional[GitRepoDTO]:
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> Optional[GitRepoDTO]:
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
