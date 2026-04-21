"""
JWT handler implementation for infrastructure layer.

This module provides the JWTHandler class, which implements JWT token creation and verification using environment configuration and the jose library.

Classes:
    JWTHandler: Implements JWT creation and verification for authentication.
"""

import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from jose import JWTError, jwt, ExpiredSignatureError
from dotenv import load_dotenv
from jose.exceptions import JWTClaimsError

from backend.src.domain.exceptions.app_exception import AppException
from backend.src.domain.exceptions.member_not_found_exception import MemberNotFoundException
from backend.src.domain.exceptions.missing_env_variable_exception import MissingEnvVariableException
from backend.src.domain.exceptions.invalid_token_exception import InvalidTokenException
from backend.src.domain.ports.repositories.i_member_repository import IMemberRepository
from backend.src.domain.ports.services.i_jwt_handler import IJWTHandler

logger = logging.getLogger(__name__)

_BACKEND_DIR = Path(__file__).resolve().parents[3]
_DOTENV_PATH = _BACKEND_DIR / ".env"


class JWTHandler(IJWTHandler):
    """
    Implementation of IJWTHandler for creating and verifying JWT tokens.

    Attributes:
        secret_key (str): Secret key for signing JWTs.
        algorithm (str): Algorithm used for JWT encoding/decoding.
        access_token_expire_minutes (int): Expiration time for access tokens (minutes).
        refresh_token_expire_days (int): Expiration time for refresh tokens (days).
    """

    def __init__(self, member_repo: IMemberRepository):
        """
        Initialize the JWTHandler.

        Loads environment variables and sets up JWT configuration.

        Raises:
            MissingEnvVariableException: If required environment variables are missing or invalid.
        """
        load_dotenv(_DOTENV_PATH)
        self.secret_key = os.getenv("JWT_SECRET_KEY")
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.member_repo = member_repo

        try:
            self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
            self.refresh_token_expire_days = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
        except ValueError as e:
            logger.exception("Invalid JWT config values.")
            raise MissingEnvVariableException(
                "ACCESS_TOKEN_EXPIRE_MINUTES or REFRESH_TOKEN_EXPIRE_DAYS must be integers.") from e

        if not self.secret_key:
            logger.error("JWTHandler initialization failed: JWT_SECRET_KEY is missing!")
            raise MissingEnvVariableException("Missing required environment variable: JWT_SECRET_KEY")

        logger.info("JWTHandler initialized successfully.")

    def create_access_token(self, data: dict) -> str:
        """
        Generate a JWT access token.

        Args:
            data (dict): Payload containing at least keys "sub" (member_id) and "mail" (email). 

        Returns:
            str: Encoded JWT access token.

        Raises:
            InvalidTokenException: If token data is empty or encoding fails.
            AppException: For unexpected errors during token creation (e.g., runtime issues).
        """
        logger.info("Starting creating access token.")

        try:
            if not data:
                logger.error("Token data cannot be empty for access token creation.")
                raise InvalidTokenException("Token data cannot be empty.")

            to_encode = data.copy()
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
            to_encode.update({"exp": expire})
            token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

            logger.info("Access token created successfully.")
            logger.info("token:%s", token)

            return token

        except JWTError as e:
            logger.exception("Failed to create access token." )
            raise InvalidTokenException("Failed to create access token.") from e
        except Exception as e:
            logger.exception("Unexpected error during create_access_token.")
            raise AppException("Unexpected error during create_access_token.") from e

    def create_refresh_token(self, data: dict) -> tuple[str, datetime]:
        """
        Generate a JWT refresh token.

        Args:
            data (dict): Payload containing at least keys "sub" (member_id) and "mail" (email).

        Returns:
            tuple[str, datetime]: Encoded JWT refresh token and its expiration datetime.

        Raises:
            InvalidTokenException: If token data is empty or encoding fails.
            AppException: For unexpected errors during token creation (e.g., runtime issues).
        """
        logger.info("Starting creating refresh token.")

        try:
            if not data:
                logger.error("Token data cannot be empty for refresh token creation.")
                raise InvalidTokenException("Token data cannot be empty.")

            to_encode = data.copy()
            expire_at = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)
            to_encode.update({"exp": expire_at, "type": "refresh"})
            token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

            logger.info("Refreshing token created successfully.")

            return token, expire_at

        except JWTError as e:
            logger.exception("Failed to create refresh token.")
            raise InvalidTokenException("Failed to create refresh token.") from e
        except Exception as e:
            logger.exception("Unexpected error during create_refresh_token.")
            raise AppException("Unexpected error during create_refresh_token.") from e

    def verify_token(self, token: str) -> dict:
        """
        Decode and verify a JWT token.

        Args:
            token (str): The JWT token to verify.

        Returns:
            dict: Decoded payload if verification is successful.

        Raises:
            InvalidTokenException: If the token is empty, expired, has invalid claims, or verification fails.
            AppException: For unexpected errors during token verification (e.g., runtime issues).
        """
        logger.info("Starting verifying token.")

        try:
            if not token:
                logger.error("Token cannot be empty for verification.")
                raise InvalidTokenException("Token cannot be empty.")
            logger.info("token:%s", token)

            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            member_id = payload.get("sub")
            email = payload.get("mail")

            if not member_id or not email:
                logger.error("Token missing required claims.")
                raise InvalidTokenException("Token missing required claims.")

            try:
                member = self.member_repo.find_by_id(member_id)

            except MemberNotFoundException:
                logger.warning("Token invalid: member not found (id=%s).", member_id)
                raise InvalidTokenException("Token invalid: member does not exist.")

            logger.info("Token verified successfully (member_id=%s).", payload.get("sub"))

            return payload

        except ExpiredSignatureError as e:
            logger.warning("Token has expired.")
            raise InvalidTokenException("Token has expired.") from e
        except JWTClaimsError as e:
            logger.warning("Invalid token claims.")
            raise InvalidTokenException("Invalid token claims.") from e
        except JWTError as e:
            logger.warning("Token verification failed.")
            raise InvalidTokenException("Invalid token.") from e
        except Exception as e:
            logger.exception("Unexpected error during verify_token.")
            raise AppException("Unexpected error during verify_token.") from e
