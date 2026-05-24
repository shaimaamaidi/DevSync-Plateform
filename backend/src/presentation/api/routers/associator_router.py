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
from starlette import status

from backend.src.domain.entities.associator import (
    AssociateClickUpSpaceRequest,
    AssociateClickUpSpaceResponse,
    AssociateMembersResponse,
    RepoMembersRequest,
)
from backend.src.infrastructure.di.persistence_container import PersistenceContainer
from backend.src.presentation.api.deps import get_persistence_container


logger = logging.getLogger(__name__)


router = APIRouter()


@router.post(
    "/space",
    response_model=AssociateClickUpSpaceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Associate a ClickUp space with a repository",
    description=(
        "Validate and link an existing ClickUp space to a repository. "
        "Ensures that the provided space code exists and persists the association."
    )
)
def associate_space(
    request: AssociateClickUpSpaceRequest,
    container: PersistenceContainer = Depends(get_persistence_container),
) -> AssociateClickUpSpaceResponse:
    """
    Associate a ClickUp space with a repository.

    Args:
        request (AssociateClickUpSpaceRequest): The association request payload.
        container (PersistenceContainer): Dependency injection container.

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


@router.post(
    "/members",
    response_model=AssociateMembersResponse,
    status_code=status.HTTP_200_OK,
    summary="Replace repository members",
    description=(
        "Replaces all existing members of a repository with the provided member list. "
        "This operation overwrites previous members."
    )
)
def associate_members(
    request: RepoMembersRequest,
    container: PersistenceContainer = Depends(get_persistence_container),
) -> AssociateMembersResponse:
    """
    Replace repository members with the provided list.

    Args:
        request (RepoMembersRequest): The request containing repository and member list.
        container (PersistenceContainer): Dependency injection container.

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


@router.post(
    "/members/add",
    response_model=AssociateMembersResponse,
    status_code=status.HTTP_200_OK,
    summary="Add members to a repository",
    description=(
        "Adds new members to a repository without removing existing ones. "
        "Only new members are appended."
    )
)
def add_members(
    request: RepoMembersRequest,
    container: PersistenceContainer = Depends(get_persistence_container),
) -> AssociateMembersResponse:
    """
    Add members to a repository.

    Args:
        request (RepoMembersRequest): The request containing repository and member list.
        container (PersistenceContainer): Dependency injection container.

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


@router.post(
    "/members/remove",
    response_model=AssociateMembersResponse,
    status_code=status.HTTP_200_OK,
    summary="Remove members from a repository",
    description=(
        "Removes specified members from a repository if they exist. "
        "Only the provided members are affected."
    )
)
def remove_members(
    request: RepoMembersRequest,
    container: PersistenceContainer = Depends(get_persistence_container),
) -> AssociateMembersResponse:
    """
    Remove members from a repository.

    Args:
        request (RepoMembersRequest): The request containing repository and member list.
        container (PersistenceContainer): Dependency injection container.

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
