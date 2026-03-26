import logging
from typing import List

from fastapi import APIRouter, Depends

from backend.src.domain.entities.member import MemberCreateDTO, MemberDTO, MemberUpdateDTO, MemberWithReposDTO
from backend.src.domain.entities.git_repo import GitRepoIdDTO
from backend.src.infrastructure.di.container import Container
from backend.src.presentation.api.deps import get_container


logger = logging.getLogger(__name__)


router = APIRouter()


@router.post("/", response_model=MemberDTO)
def add_member(member: MemberCreateDTO, container: Container = Depends(get_container)) -> MemberDTO:
    logger.info(
        "[Member] Creating member: mail=%s, username=%s.",
        member.mail,
        member.username,
    )

    result = container.member_service.add_member(member)

    logger.info(
        "[Member] Member created successfully: id=%s, mail=%s.",
        result.id,
        result.mail,
    )
    return result

@router.get("/by-repo/{repo_id}", response_model=List[MemberDTO])
def get_members_by_repo(repo_id: int, container: Container = Depends(get_container)) -> List[MemberDTO]:
    logger.info("[Member] Fetching members for repository: repo_id=%s.", repo_id)

    repo = container.repo_service.get_by_id(GitRepoIdDTO(id=repo_id))
    results = container.member_service.get_members_by_repo(repo)

    logger.info(
        "[Member] Retrieved %d members for repo_id=%s.",
        len(results),
        repo_id,
    )
    return results

@router.get("/all-with-repos", response_model=List[MemberWithReposDTO])
def get_all_with_repos(container: Container = Depends(get_container)) -> List[MemberWithReposDTO]:
    logger.info("[Member] Fetching all members with their repositories.")

    service = container.member_service
    results = service.get_all_with_repos()

    logger.info(
        "[Member] Retrieved %d members with repositories.",
        len(results),
    )
    return results

@router.put("/{member_id}", response_model=MemberWithReposDTO)
def update_member(member_id: int, member: MemberUpdateDTO, container: Container = Depends(get_container)) -> MemberWithReposDTO:
    logger.info("[Member] Updating member: id=%s.", member_id)

    service = container.member_service
    member.id = member_id
    result = service.update_member(member)

    logger.info(
        "[Member] Member updated successfully: id=%s.",
        member_id,
    )
    return result

@router.delete("/{member_id}", response_model=bool)
def delete_member(member_id: int, container: Container = Depends(get_container)) -> bool:
    logger.info("[Member] Deleting member: id=%s.", member_id)

    service = container.member_service
    result = service.delete(member_id)

    logger.info(
        "[Member] Member deleted successfully: id=%s.",
        member_id,
    )
    return result