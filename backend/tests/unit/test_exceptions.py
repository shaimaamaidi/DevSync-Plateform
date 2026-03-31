"""
Unit tests for domain exception classes.
"""

import pytest

from backend.src.domain.exceptions.app_exception import AppException
from backend.src.domain.exceptions.clickup_persistence_exception import ClickUpPersistenceException
from backend.src.domain.exceptions.clickup_space_not_found_exception import ClickUpSpaceNotFoundException
from backend.src.domain.exceptions.database_connection_exception import DatabaseConnectionException
from backend.src.domain.exceptions.database_initialization_exception import DatabaseInitializationException
from backend.src.domain.exceptions.database_session_exception import DatabaseSessionException
from backend.src.domain.exceptions.github_rate_limit_exception import GitHubRateLimitException
from backend.src.domain.exceptions.github_repo_not_found_exception import GitHubRepoNotFoundException
from backend.src.domain.exceptions.invalid_github_url_exception import InvalidGitHubUrlException
from backend.src.domain.exceptions.invalid_input_exception import InvalidInputException
from backend.src.domain.exceptions.invalid_member_data_exception import InvalidMemberDataException
from backend.src.domain.exceptions.member_not_found_exception import MemberNotFoundException
from backend.src.domain.exceptions.member_persistence_exception import MemberPersistenceException
from backend.src.domain.exceptions.repo_not_found_exception import RepoNotFoundException
from backend.src.domain.exceptions.repo_persistence_exception import RepoPersistenceException


@pytest.mark.parametrize(
    "exc,code,status",
    [
        (AppException("boom"), "APP_ERROR", 400),
        (ClickUpPersistenceException(), "CLICKUP_PERSISTENCE_ERROR", 500),
        (ClickUpSpaceNotFoundException(), "CLICKUP_SPACE_NOT_FOUND", 404),
        (DatabaseConnectionException(), "DB_CONNECTION_ERROR", 500),
        (DatabaseInitializationException(), "DB_INIT_ERROR", 500),
        (DatabaseSessionException(), "DB_SESSION_ERROR", 500),
        (GitHubRateLimitException(), "GITHUB_RATE_LIMIT", 429),
        (GitHubRepoNotFoundException("https://github.com/org/repo"), "GITHUB_REPO_NOT_FOUND", 404),
        (InvalidGitHubUrlException("bad-url"), "INVALID_GITHUB_URL", 400),
        (InvalidInputException(), "INVALID_INPUT", 422),
        (InvalidMemberDataException(["mail"]), "INVALID_MEMBER_DATA", 400),
        (MemberNotFoundException(), "MEMBER_NOT_FOUND", 404),
        (MemberPersistenceException(), "MEMBER_PERSISTENCE_ERROR", 500),
        (RepoNotFoundException(), "REPO_NOT_FOUND", 404),
        (RepoPersistenceException(), "REPO_PERSISTENCE_ERROR", 500),
    ],
)
def test_exception_metadata(exc, code, status) -> None:
    """
    Test that all custom exceptions have the correct code, HTTP status, and message type.
    """
    assert exc.code == code
    assert exc.http_status == status
    assert isinstance(exc.message, str)
