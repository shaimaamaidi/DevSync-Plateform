"""
Auth API routes.

This module defines API endpoints for member authentication, token refresh, and logout.

Routes:
    POST /login: Authenticate a member and return tokens.
    POST /refresh: Issue new tokens from a valid refresh token.
    POST /logout: Revoke a refresh token.
    Get /me: Get the currently authenticated member.
"""

import logging

from fastapi import APIRouter, Depends, Response, Request
from starlette import status

from backend.src.domain.entities.member import MemberAuthDTO, MemberTokensDTO, MemberDTO
from backend.src.infrastructure.config.settings import settings
from backend.src.infrastructure.di.persistence_container import PersistenceContainer
from backend.src.presentation.api.deps import get_persistence_container


logger = logging.getLogger(__name__)


router = APIRouter()


@router.post(
    "/login",
    response_model=MemberTokensDTO,
    status_code=status.HTTP_200_OK,
    summary="Authenticate a member and return access tokens",
    description=(
        "Authenticates a member using email and password credentials. "
        "Returns JWT access and refresh tokens and sets the access token in an HTTP-only cookie."
    )
)
def login(credentials: MemberAuthDTO, response: Response, container: PersistenceContainer = Depends(get_persistence_container)) -> MemberTokensDTO:
    """
    Authenticate a member and return tokens.

    Args:
        credentials (MemberAuthDTO): Member login credentials.
        response (Response): FastAPI response object (used to set cookies).
        container (PersistenceContainer): Dependency injection container.

    Returns:
        MemberTokensDTO: The authentication tokens.
    """
    logger.info("Login attempt: mail=%s.", credentials.mail)

    result = container.auth_use_case.login(credentials)

    response.set_cookie(
        key="access_token",
        value=result.access_token,
        httponly=True,
        secure=settings.SECURE,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # 30 minutes
        domain =settings.DOMAIN,
    )

    logger.info("Member logged in successfully: mail=%s.", credentials.mail)

    return result


@router.post(
    "/refresh",
    response_model=MemberTokensDTO,
    status_code=status.HTTP_200_OK,
    summary="Refresh authentication tokens",
    description=(
        "Generates new access and refresh tokens using a valid refresh token. "
        "Also updates the HTTP-only access token cookie."
    )
)
def refresh(refresh_token: str, response: Response, container: PersistenceContainer = Depends(get_persistence_container)) -> MemberTokensDTO:
    """
    Issue new tokens from a valid refresh token.

    Args:
        refresh_token (str): The refresh token string.
        response (Response): FastAPI response object (used to set cookies).
        container (PersistenceContainer): Dependency injection container.

    Returns:
        MemberTokensDTO: The new authentication tokens.
    """
    logger.info("Refresh token attempt.")

    result = container.auth_use_case.refresh(refresh_token)

    response.set_cookie(
        key="access_token",
        value=result.access_token,
        httponly=True,
        secure=settings.SECURE,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # 30 minutes
        domain=settings.DOMAIN,
    )

    logger.info("Tokens refreshed successfully.")

    return result


@router.post(
    "/logout",
    response_model=bool,
    status_code=status.HTTP_200_OK,
    summary="Logout a member by revoking refresh token",
    description=(
        "Revokes the provided refresh token and invalidates the user session. "
        "Effectively logs the member out from the system."
    )
)
def logout(refresh_token: str, container: PersistenceContainer = Depends(get_persistence_container)) -> bool:
    """
    Revoke a refresh token.

    Args:
        refresh_token (str): The refresh token string.
        container (PersistenceContainer): Dependency injection container.

    Returns:
        bool: True if logout was successful.
    """
    logger.info("Logout attempt.")

    container.auth_use_case.logout(refresh_token)

    logger.info("Member logged out successfully.")

    return True

@router.get(
    "/me",
    response_model=MemberDTO,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated member",
    description=(
        "Retrieves the profile information of the currently authenticated member "
        "based on the access token stored in the request context."
    )
)
def get_me(request: Request, container: PersistenceContainer = Depends(get_persistence_container)) -> MemberDTO:
    """
    Get the currently authenticated member.

    Args:
        request (Request): The incoming FastAPI request containing the current member payload.
        container (PersistenceContainer): Dependency injection container.

    Returns:
        MemberDTO: The authenticated member's data.
    """
    logger.info("Get current member attempt.")

    payload = getattr(request.state, "current_member", None)
    member_raw = payload.get("sub") if payload else None
    if not member_raw:
        logger.warning("Current member payload missing 'sub' claim.")
        raise Exception("Session is invalid. Please log in again.")

    member_id = int(member_raw)
    result = container.member_service.get_by_id(member_id)

    logger.info("Current member retrieved successfully: id=%s.", member_id)

    return result