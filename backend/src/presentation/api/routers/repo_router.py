"""
Repository API routes.

This module defines API endpoints for managing repositories, including creation, retrieval, update, and deletion.

Routes:
    GET /all: Return all repositories.
    GET /details: Return repositories with details.
    POST /: Create a new repository.
    GET /{repo_id}: Fetch a repository by id.
    GET /by-name/{name}: Fetch a repository by name.
    PUT /{repo_id}: Update a repository by id.
    DELETE /{repo_id}: Delete a repository by id.
"""

import logging
from typing import List

from fastapi import APIRouter, Depends

from backend.src.domain.entities.git_repo import (
    GitRepoCreateDTO,
    GitRepoDTO,
    GitRepoDetailDTO,
    GitRepoIdDTO,
    GitRepoNameDTO,
    GitRepoUpdateDTO,
)
from backend.src.infrastructure.di.container import Container
from backend.src.presentation.api.deps import get_container


logger = logging.getLogger(__name__)


router = APIRouter()


@router.get("/all", response_model=List[GitRepoDTO])
def get_all_repos(container: Container = Depends(get_container)) -> List[GitRepoDTO]:
    """
    Return all repositories.

    Args:
        container (Container): Dependency injection container.

    Returns:
        List[GitRepoDTO]: List of all repositories.
    """
    logger.info("Fetching all repositories.")

    results = container.repo_service.get_all()

    logger.info("Repositories retrieved successfully: count=%s.", len(results))

    return results


@router.get("/details", response_model=List[GitRepoDetailDTO])
def get_all_with_details(container: Container = Depends(get_container)) -> List[GitRepoDetailDTO]:
    """
    Return repositories with details.

    Args:
        container (Container): Dependency injection container.

    Returns:
        List[GitRepoDetailDTO]: List of repositories with details.
    """
    logger.info("Fetching all repositories with details.")

    results = container.repo_service.get_all_with_details()

    logger.info("Repositories with details retrieved: count=%s.", len(results))

    return results

@router.post("/", response_model=GitRepoDTO)
def add_repo(repo: GitRepoCreateDTO, container: Container = Depends(get_container)) -> GitRepoDTO:
    """
    Create a new repository.

    Args:
        repo (GitRepoCreateDTO): The repository creation payload.
        container (Container): Dependency injection container.

    Returns:
        GitRepoDTO: The created repository.
    """
    logger.info(
        "Creating or updating repository: name=%s, url=%s.",
    
        repo.name,
        repo.url,
    )

    result = container.repo_service.add_repo(repo)

    logger.info(
        "Repository successfully saved: id=%s, url=%s.",
        result.id,
        result.url,
    )

    return result

@router.get("/{repo_id}", response_model=GitRepoDetailDTO)
def get_repo_by_id(repo_id: int, container: Container = Depends(get_container)) -> GitRepoDetailDTO:
    """
    Fetch a repository by id.

    Args:
        repo_id (int): The repository ID.
        container (Container): Dependency injection container.

    Returns:
        GitRepoDetailDTO: The repository details.
    """
    logger.info("Fetching repository by id: repo_id=%s.", repo_id)
    
    result = container.repo_service.get_by_id(repo_id)

    logger.info("Repository retrieved successfully: repo_id=%s.", repo_id)

    return result

@router.get("/by-name/{name}", response_model=GitRepoDetailDTO)
def get_repo_by_name(name: str, container: Container = Depends(get_container)) -> GitRepoDetailDTO:
    """
    Fetch a repository by name.

    Args:
        name (str): The repository name.
        container (Container): Dependency injection container.

    Returns:
        GitRepoDetailDTO: The repository details.
    """
    logger.info("Fetching repository by name: name=%s.", name)
    
    result = container.repo_service.get_by_name(name)

    logger.info("Repository retrieved successfully: name=%s.", name)

    return result



@router.put("/{repo_id}", response_model=GitRepoDetailDTO)
def update_repo(repo_id: int, repo: GitRepoUpdateDTO, container: Container = Depends(get_container)) -> GitRepoDetailDTO:
    """
    Update a repository by id.

    Args:
        repo_id (int): The repository ID.
        repo (GitRepoUpdateDTO): The update payload.
        container (Container): Dependency injection container.

    Returns:
        GitRepoDetailDTO: The updated repository details.
    """
    logger.info(
        "Updating repository: repo_id=%s, new_name=%s, new_url=%s.",
    
        repo_id,
        repo.name,
        repo.url,
    )

    repo.id = repo_id
    result = container.repo_service.update_repo(repo)

    logger.info("Repository updated successfully: repo_id=%s.", repo_id)

    return result

@router.delete("/{repo_id}", response_model=bool)
def delete_repo(repo_id: int, container: Container = Depends(get_container)) -> bool:
    """
    Delete a repository by id.

    Args:
        repo_id (int): The repository ID.
        container (Container): Dependency injection container.

    Returns:
        bool: True if deletion was successful.
    """
    logger.info("Deleting repository: repo_id=%s.", repo_id)
    
    result = container.repo_service.delete(repo_id)

    logger.info("Repository deleted successfully: repo_id=%s.", repo_id)

    return result