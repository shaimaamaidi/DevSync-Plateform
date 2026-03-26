import logging
from typing import List

from backend.src.domain.entities.git_repo import (
    GitRepoCreateDTO,
    GitRepoDTO,
    GitRepoDetailDTO,
    GitRepoIdDTO,
    GitRepoNameDTO,
    GitRepoUpdateDTO,
)
from backend.src.domain.ports.repositories.i_repo_repository import IRepoRepository


logger = logging.getLogger(__name__)


class RepoService:
    def __init__(self, repo_repo: IRepoRepository):
        self._repo = repo_repo

    def add_repo(self, repo: GitRepoCreateDTO) -> GitRepoDTO:
        logger.info("Adding new repository: name=%s, url=%s.", repo.name, repo.url)

        result = self._repo.save(repo)

        logger.info("Repository added successfully: id=%s, name=%s.", result.id, result.name)

        return result

    def update_repo(self, repo: GitRepoUpdateDTO) -> GitRepoDetailDTO:
        logger.info("Updating repository: id=%s, name=%s.", repo.id, repo.name)

        result = self._repo.update(repo)

        logger.info("Repository updated successfully: id=%s, name=%s.", result.id, result.name)
        return result

    def get_by_id(self, repo: GitRepoIdDTO) -> GitRepoDetailDTO:
        logger.info("Fetching repository by id: %s.", repo.id)

        result = self._repo.find_by_id(repo.id)

        logger.info("Repository fetched successfully: id=%s, name=%s.", result.id, result.name)
        return result

    def get_by_name(self, repo: GitRepoNameDTO) -> GitRepoDetailDTO:
        logger.info("Fetching repository by name: %s.", repo.name)

        result = self._repo.find_by_name(repo.name)

        logger.info("Repository fetched successfully: id=%s, name=%s.", result.id, result.name)
        return result

    def get_by_url(self, url: str) -> GitRepoDTO:
        logger.info("Fetching repository by URL: %s.", url)

        result = self._repo.find_by_url(url)

        logger.info("Repository fetched successfully: id=%s, url=%s.", result.id, result.url)
        return result

    def get_all(self) -> List[GitRepoDTO]:
        logger.info("Fetching all repositories.")

        results = self._repo.find_all()

        logger.info("Fetched %s repositories successfully.", len(results))
        return results

    def get_all_with_details(self) -> List[GitRepoDetailDTO]:
        logger.info("Fetching all repositories with details.")

        results = self._repo.find_all_with_details()

        logger.info("Fetched %s detailed repositories successfully.", len(results))
        return results

    def delete(self, repo: GitRepoIdDTO) -> bool:
        logger.info("Deleting repository: id=%s.", repo.id)

        result = self._repo.delete(repo.id)

        logger.info("Repository deleted successfully: id=%s.", repo.id)
        
        return result
