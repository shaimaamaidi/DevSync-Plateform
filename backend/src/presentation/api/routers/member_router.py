"""
Member API routes.

This module defines API endpoints for managing members, including creation, retrieval, update, and deletion.

Routes:
    POST /: Create a new member.
    GET /by-repo/{repo_id}: Return members for a repository.
    GET /all-with-repos: Return all members with repositories.
    PUT /{member_id}: Update a member by id.
    DELETE /{member_id}: Delete a member by id.
"""

import logging
from typing import List

from fastapi import APIRouter, Depends
from starlette import status

from backend.src.domain.entities.member import MemberCreateDTO, MemberDTO, MemberUpdateDTO, MemberWithReposDTO
from backend.src.infrastructure.di.container import Container
from backend.src.presentation.api.deps import get_container


logger = logging.getLogger(__name__)


router = APIRouter()


@router.post(
    "/",
    response_model=MemberDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new member",
    description="Creates a new member in the system using the provided data. The member is persisted and returned after successful creation."
)
def add_member(member: MemberCreateDTO, container: Container = Depends(get_container)) -> MemberDTO:
    """
    Create a new member.

    Args:
        member (MemberCreateDTO): The member creation payload.
        container (Container): Dependency injection container.

    Returns:
        MemberDTO: The created member.

    Raises:
        Exception: If creation fails (handled by global exception handler).
    """
    logger.info(
        "Creating member: mail=%s, username=%s.",
        member.mail,
        member.username,
    )

    result = container.member_service.add_member(member)

    logger.info(
        "Member created successfully: id=%s, mail=%s.",
        result.id,
        result.mail,
    )

    return result

@router.get(
    "/by-repo/{repo_id}",
    response_model=List[MemberDTO],
    status_code=status.HTTP_200_OK,
    summary="Get members by repository",
    description=(
        "Retrieves all members associated with a specific repository ID."
    )
)
def get_members_by_repo(repo_id: int, container: Container = Depends(get_container)) -> List[MemberDTO]:
    """
    Return members for a repository.

    Args:
        repo_id (int): The repository ID.
        container (Container): Dependency injection container.

    Returns:
        List[MemberDTO]: List of members for the repository.

    Raises:
        Exception: If retrieval fails (handled by global exception handler).
    """
    logger.info("Fetching members for repository: repo_id=%s.", repo_id)

    results = container.member_service.get_members_by_repo(repo_id)

    logger.info(
        "Retrieved %d members for repo_id=%s.",
        len(results),
        repo_id,
    )

    return results

@router.get(
    "/all-with-repos",
    response_model=List[MemberWithReposDTO],
    status_code=status.HTTP_200_OK,
    summary="Get all members with repositories",
    description=(
        "Retrieves all members in the system along with their associated repositories."
    )
)
def get_all_with_repos(container: Container = Depends(get_container)) -> List[MemberWithReposDTO]:
    """
    Return all members with repositories.

    Args:
        container (Container): Dependency injection container.

    Returns:
        List[MemberWithReposDTO]: List of all members with their repositories.

    Raises:
        Exception: If retrieval fails (handled by global exception handler).
    """
    logger.info("Fetching all members with their repositories.")

    results = container.member_service.get_all_with_repos()

    logger.info("Retrieved %d members with repositories.", len(results))

    return results

@router.put(
    "/{member_id}",
    response_model=MemberWithReposDTO,
    status_code=status.HTTP_200_OK,
    summary="Update a member",
    description="Updates an existing member identified by its ID with the provided data. Returns the updated member along with its repositories."
)
def update_member(member_id: int, member: MemberUpdateDTO, container: Container = Depends(get_container)) -> MemberWithReposDTO:
    """
    Update a member by id.

    Args:
        member_id (int): The member ID.
        member (MemberUpdateDTO): The update payload.
        container (Container): Dependency injection container.

    Returns:
        MemberWithReposDTO: The updated member with repositories.

    Raises:
        Exception: If update fails (handled by global exception handler).
    """
    logger.info("Updating member: id=%s.", member_id)

    member_with_id: MemberUpdateDTO = member.model_copy(update={"id": member_id})

    result = container.member_service.update_member(member_with_id)

    logger.info("Member updated successfully: id=%s.", member_id)

    return result

@router.delete(
    "/{member_id}",
    response_model=bool,
    status_code=status.HTTP_200_OK,
    summary="Delete a member",
    description="Deletes a member by its ID. Returns a boolean indicating whether the operation was successful."
)
def delete_member(member_id: int, container: Container = Depends(get_container)) -> bool:
    """
    Delete a member by id.

    Args:
        member_id (int): The member ID.
        container (Container): Dependency injection container.

    Returns:
        bool: True if deletion was successful.

    Raises:
        Exception: If deletion fails (handled by global exception handler).
    """
    logger.info("Deleting member: id=%s.", member_id)
    
    result = container.member_service.delete(member_id)

    logger.info("Member deleted successfully: id=%s.",member_id,)

    return result