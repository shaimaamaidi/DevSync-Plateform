"""
Associator API routes.

This module defines API endpoints for associating ClickUp spaces and members with repositories.

Routes:
    POST /space: Associate a ClickUp space with a repository.
    POST /members: Replace repository members with a provided list.
    POST /members/add: Add members to a repository.
    POST /members/remove: Remove members from a repository.
"""

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
    """
    Associate a ClickUp space with a repository.

    Args:
        request (AssociateClickUpSpaceRequest): The association request payload.
        container (Container): Dependency injection container.

    Returns:
        AssociateClickUpSpaceResponse: The association result.
    """
    logger.info(
        "Associating ClickUp space with repository: repo_url=%s, space_code=%s.",
        request.repo_url,
        request.space_code,
    )

    service = container.associator_use_case
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
    """
    Replace repository members with the provided list.

    Args:
        request (RepoMembersRequest): The request containing repository and member list.
        container (Container): Dependency injection container.

    Returns:
        AssociateMembersResponse: The association result.
    """
    logger.info(
        "Associating members with repository: repo_url=%s, members_count=%s.",
        request.repo_url,
        len(request.members),
    )

    service = container.associator_use_case
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
    """
    Add members to a repository.

    Args:
        request (RepoMembersRequest): The request containing repository and member list.
        container (Container): Dependency injection container.

    Returns:
        AssociateMembersResponse: The result of adding members.
    """
    logger.info(
        "Adding members to repository: repo_url=%s, members_count=%s.",
        request.repo_url,
        len(request.members),
    )

    service = container.associator_use_case
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
    """
    Remove members from a repository.

    Args:
        request (RepoMembersRequest): The request containing repository and member list.
        container (Container): Dependency injection container.

    Returns:
        AssociateMembersResponse: The result of removing members.
    """
    logger.info(
        "Removing members from repository: repo_url=%s, members_count=%s.",
        request.repo_url,
        len(request.members),
    )

    service = container.associator_use_case
    result = service.remove_members(request)

    logger.info(
        "Members removed successfully: repo_url=%s, members_count=%s.",
        request.repo_url,
        len(request.members),
    )

    return result
