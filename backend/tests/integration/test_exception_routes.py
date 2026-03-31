"""
Integration tests for exception-to-response mapping.
"""

import pytest
from fastapi.testclient import TestClient

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
    "service_name,method,http_method,path,payload,params,exc,status,code",
    [
        (
            "repo_service",
            "get_all",
            "GET",
            "/repo/all",
            None,
            None,
            AppException("boom"),
            400,
            "APP_ERROR",
        ),
        (
            "repo_service",
            "get_by_id",
            "GET",
            "/repo/99",
            None,
            None,
            RepoNotFoundException("missing"),
            404,
            "REPO_NOT_FOUND",
        ),
        (
            "repo_service",
            "add_repo",
            "POST",
            "/repo/",
            {"name": "repo", "url": "https://github.com/org/repo"},
            None,
            RepoPersistenceException(),
            500,
            "REPO_PERSISTENCE_ERROR",
        ),
        (
            "repo_service",
            "update_repo",
            "PUT",
            "/repo/1",
            {"name": "new"},
            None,
            InvalidInputException("bad"),
            422,
            "INVALID_INPUT",
        ),
        (
            "member_service",
            "delete",
            "DELETE",
            "/member/1",
            None,
            None,
            MemberNotFoundException("missing"),
            404,
            "MEMBER_NOT_FOUND",
        ),
        (
            "member_service",
            "add_member",
            "POST",
            "/member/",
            {"username": "alice", "mail": "a@b.com"},
            None,
            MemberPersistenceException(),
            500,
            "MEMBER_PERSISTENCE_ERROR",
        ),
        (
            "clickup_service",
            "get_by_id",
            "GET",
            "/clickup/1",
            None,
            None,
            ClickUpSpaceNotFoundException("missing"),
            404,
            "CLICKUP_SPACE_NOT_FOUND",
        ),
        (
            "clickup_service",
            "add_space",
            "POST",
            "/clickup/",
            {"name": "Platform", "space_code": "PLT"},
            None,
            ClickUpPersistenceException(),
            500,
            "CLICKUP_PERSISTENCE_ERROR",
        ),
        (
            "associator_service",
            "add_members",
            "POST",
            "/associate/members/add",
            {"repo_url": "https://github.com/org/repo", "members": [{"mail": "a@b.com"}]},
            None,
            InvalidMemberDataException(["mail"]),
            400,
            "INVALID_MEMBER_DATA",
        ),
        (
            "deployment_service",
            "list_deployments",
            "GET",
            "/deployment/list",
            None,
            {"repo_url": "bad"},
            InvalidGitHubUrlException("bad"),
            400,
            "INVALID_GITHUB_URL",
        ),
        (
            "deployment_service",
            "list_deployments",
            "GET",
            "/deployment/list",
            None,
            {"repo_url": "https://github.com/org/repo"},
            GitHubRepoNotFoundException("https://github.com/org/repo"),
            404,
            "GITHUB_REPO_NOT_FOUND",
        ),
        (
            "deployment_service",
            "list_deployments",
            "GET",
            "/deployment/list",
            None,
            {"repo_url": "https://github.com/org/repo"},
            GitHubRateLimitException("12:00:00"),
            429,
            "GITHUB_RATE_LIMIT",
        ),
        (
            "repo_service",
            "get_all_with_details",
            "GET",
            "/repo/details",
            None,
            None,
            DatabaseConnectionException(),
            500,
            "DB_CONNECTION_ERROR",
        ),
        (
            "clickup_service",
            "get_all",
            "GET",
            "/clickup/",
            None,
            None,
            DatabaseInitializationException(),
            500,
            "DB_INIT_ERROR",
        ),
        (
            "member_service",
            "get_all_with_repos",
            "GET",
            "/member/all-with-repos",
            None,
            None,
            DatabaseSessionException(),
            500,
            "DB_SESSION_ERROR",
        ),
    ],
)
def test_exception_routes(
    client: TestClient,
    container,
    service_name,
    method,
    http_method,
    path,
    payload,
    params,
    exc,
    status,
    code,
) -> None:
    """
    Test that exceptions raised by services are mapped to the correct HTTP status and error code in the API response.
    """
    service = getattr(container, service_name)
    getattr(service, method).side_effect = exc

    response = client.request(http_method, path, json=payload, params=params)

    assert response.status_code == status
    assert response.json()["error"]["code"] == code
