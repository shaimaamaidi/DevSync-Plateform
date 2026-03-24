from fastapi import APIRouter, Depends
from typing import List

from backend.src.domain.entities.member import MemberDTO, MemberWithReposDTO
from backend.src.infrastructure.di.container import Container
from backend.src.presentation.api.deps import get_container

router = APIRouter()


@router.post("/")
def add_member(member: MemberDTO, container: Container = Depends(get_container)) -> MemberDTO:
    return container.member_service.add_member(member)


@router.get("/by-repo/{repo_id}")
def get_members_by_repo(repo_id: int, container: Container = Depends(get_container)) -> List[MemberDTO]:
    repo = container.repo_service.get_by_id(repo_id)
    return container.member_service.get_members_by_repo(repo)


@router.get("/all-with-repos")
def get_all_with_repos(container: Container = Depends(get_container)) -> List[MemberWithReposDTO]:
    service = container.member_service
    return service.get_all_with_repos()


@router.put("/{member_id}")
def update_member(member_id: int, member: MemberDTO, container: Container = Depends(get_container)) -> MemberDTO:
    service = container.member_service
    member.id = member_id
    return service.update_member(member)


@router.delete("/{member_id}")
def delete_member(member_id: int, container: Container = Depends(get_container)) -> bool:
    service = container.member_service
    return service.delete(member_id)