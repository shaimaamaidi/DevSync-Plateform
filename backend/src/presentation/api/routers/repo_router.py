from fastapi import APIRouter, Request
from typing import List

from backend.src.domain.entities.git_repo import GitRepoDTO, GitRepoDetailDTO

router = APIRouter()


@router.get("/all")
def get_all_repos(request: Request) -> List[GitRepoDTO]:
    service = request.app.state.container.repo_service
    return service.get_all()


@router.get("/details")
def get_all_with_details(request: Request) -> List[GitRepoDetailDTO]:
    service = request.app.state.container.repo_service
    return service.get_all_with_details()


@router.post("/")
def add_repo(request: Request, repo: GitRepoDTO) -> GitRepoDTO:
    service = request.app.state.container.repo_service
    return service.add_repo(repo)


@router.get("/{repo_id}")
def get_repo_by_id(repo_id: int, request: Request) -> GitRepoDTO:
    service = request.app.state.container.repo_service
    return service.get_by_id(repo_id)


@router.get("/by-name/{name}")
def get_repo_by_name(name: str, request: Request) -> GitRepoDTO:
    service = request.app.state.container.repo_service
    return service.get_by_name(name)


@router.put("/{repo_id}")
def update_repo(repo_id: int, request: Request, repo: GitRepoDTO) -> GitRepoDTO:
    service = request.app.state.container.repo_service
    repo.id = repo_id
    return service.update_repo(repo)


@router.delete("/{repo_id}")
def delete_repo(repo_id: int, request: Request) -> bool:
    service = request.app.state.container.repo_service
    return service.delete(repo_id)