"""Associator API routes."""

import logging
from fastapi import APIRouter, Depends

from backend.src.domain.entities.associator import (
    AssociateClickUpSpaceRequest,
    AssociateClickUpSpaceResponse,
    AssociateMembersResponse,
    RepoMembersRequest,
)
from backend.src.infrastructure.di.container import Container
from backend.src.presentation.api.deps import get_container


logger = logging.getLogger(__name__)


router = APIRouter()


@router.post("/space", response_model=AssociateClickUpSpaceResponse)
def associate_space(
    request: AssociateClickUpSpaceRequest,
    container: Container = Depends(get_container),
) -> AssociateClickUpSpaceResponse:
    """Associate a ClickUp space with a repository."""
    logger.info(
        "Associating ClickUp space with repository: repo_url=%s, space_code=%s.",
        request.repo_url,
        request.space_code,
    )

    service = container.associator_service
    result = service.associate_clickup_space(request)

    logger.info(
        "ClickUp space associated successfully: repo_url=%s, space_code=%s.",
        request.repo_url,
        request.space_code,
    )

    return result


@router.post("/members", response_model=AssociateMembersResponse)
def associate_members(
    request: RepoMembersRequest,
    container: Container = Depends(get_container),
) -> AssociateMembersResponse:
    """Replace repository members with the provided list."""
    logger.info(
        "Associating members with repository: repo_url=%s, members_count=%s.",
        request.repo_url,
        len(request.members),
    )

    service = container.associator_service
    results = service.update_members(request)

    logger.info(
        "Members associated successfully: repo_url=%s, members_count=%s.",
        request.repo_url,
        len(request.members),
    )

    return results


@router.post("/members/add", response_model=AssociateMembersResponse)
def add_members(
    request: RepoMembersRequest,
    container: Container = Depends(get_container),
) -> AssociateMembersResponse:
    """Add members to a repository."""
    logger.info(
        "Adding members to repository: repo_url=%s, members_count=%s.",
        request.repo_url,
        len(request.members),
    )

    service = container.associator_service
    result = service.add_members(request)

    logger.info(
        "Members added successfully: repo_url=%s, members_count=%s.",
        request.repo_url,
        len(request.members),
    )

    return result


@router.post("/members/remove", response_model=AssociateMembersResponse)
def remove_members(
    request: RepoMembersRequest,
    container: Container = Depends(get_container),
) -> AssociateMembersResponse:
    """Remove members from a repository."""
    logger.info(
        "Removing members from repository: repo_url=%s, members_count=%s.",
        request.repo_url,
        len(request.members),
    )

    service = container.associator_service
    result = service.remove_members(request)

    logger.info(
        "Members removed successfully: repo_url=%s, members_count=%s.",
        request.repo_url,
        len(request.members),
    )

    return result
