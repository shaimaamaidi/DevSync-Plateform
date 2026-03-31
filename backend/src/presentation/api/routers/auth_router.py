"""
Auth API routes.

This module defines API endpoints for member authentication, token refresh, and logout.

Routes:
    POST /login: Authenticate a member and return tokens.
    POST /refresh: Issue new tokens from a valid refresh token.
    POST /logout: Revoke a refresh token.
"""

import logging

from fastapi import APIRouter, Depends

from backend.src.domain.entities.member import MemberAuthDTO, MemberTokensDTO
from backend.src.infrastructure.di.container import Container
from backend.src.presentation.api.deps import get_container


logger = logging.getLogger(__name__)


router = APIRouter()


@router.post("/login", response_model=MemberTokensDTO)
def login(credentials: MemberAuthDTO, container: Container = Depends(get_container)) -> MemberTokensDTO:
    """
    Authenticate a member and return tokens.

    Args:
        credentials (MemberAuthDTO): Member login credentials.
        container (Container): Dependency injection container.

    Returns:
        MemberTokensDTO: The authentication tokens.
    """
    logger.info("Login attempt: mail=%s.", credentials.mail)

    result = container.auth_service.login(credentials)

    logger.info("Member logged in successfully: mail=%s.", credentials.mail)

    return result


@router.post("/refresh", response_model=MemberTokensDTO)
def refresh(refresh_token: str, container: Container = Depends(get_container)) -> MemberTokensDTO:
    """
    Issue new tokens from a valid refresh token.

    Args:
        refresh_token (str): The refresh token string.
        container (Container): Dependency injection container.

    Returns:
        MemberTokensDTO: The new authentication tokens.
    """
    logger.info("Refresh token attempt.")

    result = container.auth_service.refresh(refresh_token)

    logger.info("Tokens refreshed successfully.")

    return result


@router.post("/logout", response_model=bool)
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

    container.auth_service.logout(refresh_token)

    logger.info("Member logged out successfully.")

    return True