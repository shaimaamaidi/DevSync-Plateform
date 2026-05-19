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

from backend.src.domain.exceptions.base.app_exception import AppException
from backend.src.domain.exceptions.common.missing_env_variable_exception import MissingEnvVariableException
from backend.src.domain.exceptions.auth.invalid_token_exception import InvalidTokenException
from backend.src.domain.ports.output.i_jwt_handler import IJWTHandler

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

    def __init__(self):
        """
        Initialize the JWTHandler.

        Loads environment variables and sets up JWT configuration.

        Raises:
            MissingEnvVariableException: If required environment variables are missing or invalid.
        """
        load_dotenv(_DOTENV_PATH)
        self.secret_key = os.getenv("JWT_SECRET_KEY")
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")

        if not self.secret_key:
            logger.error("JWTHandler initialization failed: JWT_SECRET_KEY is missing!")
            raise MissingEnvVariableException()

        try:
            self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
            self.refresh_token_expire_days = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
        except ValueError as e:
            logger.exception("Invalid JWT config values.")
            raise MissingEnvVariableException()

        logger.info("JWTHandler initialized successfully.")

    def create_access_token(self, data: dict) -> str:
        """
        Generate a JWT access token.

        Args:
            data (dict): Payload containing at least keys "sub" (member_id) and "mail" (email).

        Returns:
            str: Encoded JWT access token.

        Raises:
            InvalidTokenException: If session is invalid.
            AppException: For unexpected errors during token creation (e.g., runtime issues).
        """
        logger.info("Starting creating access token.")

        try:
            if not data:
                logger.error("Token data cannot be empty for access token creation.")
                raise InvalidTokenException("Session is invalid. Please log in again.")

            to_encode = data.copy()
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
            to_encode.update({"exp": expire})
            token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

            logger.info("Access token created successfully.")

            return token

        except JWTError as e:
            logger.exception("Failed to create access token." )
            raise InvalidTokenException("Unable to start your session. Please try again.")
        except Exception as e:
            logger.exception("Unexpected error during create_access_token.")
            raise AppException("Something went wrong. Please try again later.")

    def create_refresh_token(self, data: dict) -> tuple[str, datetime]:
        """
        Generate a JWT refresh token.

        Args:
            data (dict): Payload containing at least keys "sub" (member_id) and "mail" (email).

        Returns:
            tuple[str, datetime]: Encoded JWT refresh token and its expiration datetime.

        Raises:
            InvalidTokenException: If session is invalid.
            AppException: For unexpected errors during token creation (e.g., runtime issues).
        """
        logger.info("Starting creating refresh token.")

        try:
            if not data:
                logger.error("Token data cannot be empty for refresh token creation.")
                raise InvalidTokenException("Session is invalid. Please log in again.")

            to_encode = data.copy()
            expire_at = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)
            to_encode.update({"exp": expire_at, "type": "refresh"})
            token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

            logger.info("Refreshing token created successfully.")

            return token, expire_at

        except JWTError as e:
            logger.exception("Failed to create refresh token.")
            raise InvalidTokenException("Unable to start your session. Please try again.")
        except Exception as e:
            logger.exception("Unexpected error during create_refresh_token.")
            raise AppException("Something went wrong. Please try again later.")

    def verify_token(self, token: str) -> dict:
        """
        Decode and verify a JWT token.

        Args:
            token (str): The JWT token to verify.

        Returns:
            dict: Decoded payload if verification is successful.

        Raises:
            InvalidTokenException: If session is invalid or expired.
            AppException: For unexpected errors during token verification (e.g., runtime issues).
        """
        logger.info("Starting verifying token.")

        try:
            if not token:
                logger.error("Token cannot be empty for verification.")
                raise InvalidTokenException("Session is invalid. Please log in again.")

            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            member_id = payload.get("sub")
            email = payload.get("mail")

            if not member_id or not email:
                logger.error("Token missing required claims.")
                raise InvalidTokenException("Session is invalid. Please log in again.")

            logger.info("Token verified successfully (member_id=%s).", payload.get("sub"))

            return payload

        except ExpiredSignatureError as e:
            logger.warning("Token has expired.")
            raise InvalidTokenException("Session is expired. Please log in again.") from e
        except JWTClaimsError as e:
            logger.warning("Invalid token claims.")
            raise InvalidTokenException("Session is invalid. Please log in again.") from e
        except JWTError as e:
            logger.warning("Token verification failed.")
            raise InvalidTokenException("Session is invalid. Please log in again.") from e
        except Exception as e:
            logger.exception("Unexpected error during verify_token.")
            raise AppException("Something went wrong. Please try again later.")
