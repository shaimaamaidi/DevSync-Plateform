import logging
from typing import List

from fastapi import APIRouter, Depends

from backend.src.domain.entities.git_repo import GitRepoDTO
from backend.src.domain.entities.clickup_space import ClickUpSpaceDTO
from backend.src.infrastructure.di.container import Container
from backend.src.presentation.api.deps import get_container


logger = logging.getLogger(__name__)


router = APIRouter()


@router.post("/space")
def associate_space(
    repo: GitRepoDTO,
    clickup_space: ClickUpSpaceDTO,
    container: Container = Depends(get_container),
):
    logger.info(
        "Associating ClickUp space with repository: repo_url=%s, space_id=%s",
        repo.url,
        clickup_space.space_id,
    )

    service = container.associator_service
    result = service.associate_space(repo, clickup_space)

    logger.info(
        "ClickUp space associated successfully: repo_url=%s, space_id=%s",
        repo.url,
        clickup_space.space_id,
    )
    return result

@router.post("/members")
def associate_members(
    repo: GitRepoDTO,
    members: List[dict],
    container: Container = Depends(get_container),
):
    logger.info(
        "Associating members with repository: repo_url=%s, members_count=%s",
        repo.url,
        len(members),
    )

    service = container.associator_service
    results = service.associate_members(repo, members)

    logger.info(
        "Members associated successfully: repo_url=%s, members_count=%s",
        repo.url,
        len(results),
    )
    return results