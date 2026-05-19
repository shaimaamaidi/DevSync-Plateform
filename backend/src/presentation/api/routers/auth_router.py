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
from backend.src.infrastructure.di.container import Container
from backend.src.presentation.api.deps import get_container


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
def login(credentials: MemberAuthDTO, response: Response, container: Container = Depends(get_container)) -> MemberTokensDTO:
    """
    Authenticate a member and return tokens.

    Args:
        credentials (MemberAuthDTO): Member login credentials.
        response (Response): FastAPI response object (used to set cookies).
        container (Container): Dependency injection container.

    Returns:
        MemberTokensDTO: The authentication tokens.
    """
    logger.info("Login attempt: mail=%s.", credentials.mail)

    result = container.auth_use_case.login(credentials)

    response.set_cookie(
        key="access_token",
        value=result.access_token,
        httponly=True,
        secure=False,  # False en local, à remettre à True en prod
        samesite="lax",
        max_age=30*60,  # 30 minutes
        domain = "localhost",
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
def refresh(refresh_token: str, response: Response, container: Container = Depends(get_container)) -> MemberTokensDTO:
    """
    Issue new tokens from a valid refresh token.

    Args:
        refresh_token (str): The refresh token string.
        response (Response): FastAPI response object (used to set cookies).
        container (Container): Dependency injection container.

    Returns:
        MemberTokensDTO: The new authentication tokens.
    """
    logger.info("Refresh token attempt.")

    result = container.auth_use_case.refresh(refresh_token)

    response.set_cookie(
        key="access_token",
        value=result.access_token,
        httponly=True,
        secure=False,  # False en local, à remettre à True en prod
        samesite="lax",
        max_age=30*60,  # 30 minutes
        domain="localhost",
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
def logout(refresh_token: str, container: Container = Depends(get_container)) -> bool:
    """
    Revoke a refresh token.

    Args:
        refresh_token (str): The refresh token string.
        container (Container): Dependency injection container.

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
def get_me(request: Request, container: Container = Depends(get_container)) -> MemberDTO:
    """
    Get the currently authenticated member.

    Args:
        request (Request): The incoming FastAPI request containing the current member payload.
        container (Container): Dependency injection container.

    Returns:
        MemberDTO: The authenticated member's data.
    """
    logger.info("Get current member attempt.")

    payload = request.state.current_member
    member_id = int(payload.get("sub"))
    result = container.member_service.get_by_id(member_id)

    logger.info("Current member retrieved successfully: id=%s.", member_id)

    return result