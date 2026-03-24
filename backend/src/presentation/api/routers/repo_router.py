from fastapi import APIRouter, Depends
from typing import List

from backend.src.domain.entities.git_repo import GitRepoDTO, GitRepoDetailDTO
from backend.src.infrastructure.di.container import Container
from backend.src.presentation.api.deps import get_container

router = APIRouter()


@router.get("/all")
def get_all_repos(container: Container = Depends(get_container)) -> List[GitRepoDTO]:
    service = container.repo_service
    return service.get_all()


@router.get("/details")
def get_all_with_details(container: Container = Depends(get_container)) -> List[GitRepoDetailDTO]:
    service = container.repo_service
    return service.get_all_with_details()


@router.post("/")
def add_repo(repo: GitRepoDTO, container: Container = Depends(get_container)) -> GitRepoDTO:
    service = container.repo_service
    return service.add_repo(repo)


@router.get("/{repo_id}")
def get_repo_by_id(repo_id: int, container: Container = Depends(get_container)) -> GitRepoDTO:
    service = container.repo_service
    return service.get_by_id(repo_id)


@router.get("/by-name/{name}")
def get_repo_by_name(name: str, container: Container = Depends(get_container)) -> GitRepoDTO:
    service = container.repo_service
    return service.get_by_name(name)


@router.put("/{repo_id}")
def update_repo(repo_id: int, repo: GitRepoDTO, container: Container = Depends(get_container)) -> GitRepoDTO:
    service = container.repo_service
    repo.id = repo_id
    return service.update_repo(repo)


@router.delete("/{repo_id}")
def delete_repo(repo_id: int, container: Container = Depends(get_container)) -> bool:
    service = container.repo_service
    return service.delete(repo_id)