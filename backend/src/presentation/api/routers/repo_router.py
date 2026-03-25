import logging
from typing import List

from fastapi import APIRouter, Depends

from backend.src.domain.entities.git_repo import GitRepoDTO, GitRepoDetailDTO
from backend.src.infrastructure.di.container import Container
from backend.src.presentation.api.deps import get_container


logger = logging.getLogger(__name__)


router = APIRouter()


@router.get("/all")
def get_all_repos(container: Container = Depends(get_container)) -> List[GitRepoDTO]:
    logger.info("Fetching all repositories")

    service = container.repo_service
    results = service.get_all()

    logger.info("Repositories retrieved successfully: count=%s", len(results))
    return results

@router.get("/details")
def get_all_with_details(container: Container = Depends(get_container)) -> List[GitRepoDetailDTO]:
    logger.info("Fetching all repositories with details")

    service = container.repo_service
    results = service.get_all_with_details()

    logger.info("Repositories with details retrieved: count=%s", len(results))
    return results

@router.post("/")
def add_repo(repo: GitRepoDTO, container: Container = Depends(get_container)) -> GitRepoDTO:
    logger.info(
        "Creating or updating repository: name=%s, url=%s",
        repo.name,
        repo.url,
    )

    service = container.repo_service
    result = service.add_repo(repo)

    logger.info(
        "Repository successfully saved: id=%s, url=%s",
        result.id,
        result.url,
    )
    return result

@router.get("/{repo_id}")
def get_repo_by_id(repo_id: int, container: Container = Depends(get_container)) -> GitRepoDTO:
    logger.info("Fetching repository by id: repo_id=%s", repo_id)

    service = container.repo_service
    result = service.get_by_id(repo_id)

    logger.info("Repository retrieved successfully: repo_id=%s", repo_id)
    return result

@router.get("/by-name/{name}")
def get_repo_by_name(name: str, container: Container = Depends(get_container)) -> GitRepoDTO:
    logger.info("Fetching repository by name: name=%s", name)

    service = container.repo_service
    result = service.get_by_name(name)

    logger.info("Repository retrieved successfully: name=%s", name)
    return result



@router.put("/{repo_id}")
def update_repo(repo_id: int, repo: GitRepoDTO, container: Container = Depends(get_container)) -> GitRepoDTO:
    logger.info(
        "Updating repository: repo_id=%s, new_name=%s, new_url=%s",
        repo_id,
        repo.name,
        repo.url,
    )

    service = container.repo_service
    repo.id = repo_id
    result = service.update_repo(repo)

    logger.info("Repository updated successfully: repo_id=%s", repo_id)
    return result

@router.delete("/{repo_id}")
def delete_repo(repo_id: int, container: Container = Depends(get_container)) -> bool:
    logger.info("Deleting repository: repo_id=%s", repo_id)

    service = container.repo_service
    result = service.delete(repo_id)

    logger.info("Repository deleted successfully: repo_id=%s", repo_id)
    return result