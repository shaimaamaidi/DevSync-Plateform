from fastapi import APIRouter, Request
from typing import List

from backend.src.domain.entities.member import MemberDTO, MemberWithReposDTO

router = APIRouter()


@router.post("/")
def add_member(request: Request, username: str, email: str, repo_id: int) -> MemberDTO:
    container = request.app.state.container
    repo = container.repo_service.get_by_id(repo_id)
    return container.member_service.add_member(username, email, repo)


@router.get("/by-repo/{repo_id}")
def get_members_by_repo(repo_id: int, request: Request) -> List[MemberDTO]:
    container = request.app.state.container
    repo = container.repo_service.get_by_id(repo_id)
    return container.member_service.get_members_by_repo(repo)


@router.get("/all-with-repos")
def get_all_with_repos(request: Request) -> List[MemberWithReposDTO]:
    service = request.app.state.container.member_service
    return service.get_all_with_repos()


@router.put("/{member_id}")
def update_member(member_id: int, request: Request, username: str = None, email: str = None) -> MemberDTO:
    service = request.app.state.container.member_service
    return service.update(member_id, username, email)


@router.delete("/{member_id}")
def delete_member(member_id: int, request: Request) -> bool:
    service = request.app.state.container.member_service
    return service.delete(member_id)