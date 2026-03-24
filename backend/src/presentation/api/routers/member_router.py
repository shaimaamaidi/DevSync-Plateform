from fastapi import APIRouter, Request
from typing import List

from backend.src.domain.entities.member import MemberDTO, MemberWithReposDTO

router = APIRouter()


@router.post("/")
def add_member(request: Request, member: MemberDTO) -> MemberDTO:
    container = request.app.state.container
    return container.member_service.add_member(member)


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
def update_member(member_id: int, request: Request, member: MemberDTO) -> MemberDTO:
    service = request.app.state.container.member_service
    member.id = member_id
    return service.update_member(member)


@router.delete("/{member_id}")
def delete_member(member_id: int, request: Request) -> bool:
    service = request.app.state.container.member_service
    return service.delete(member_id)