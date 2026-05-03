"""
Shared pytest fixtures for backend tests.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient

from backend.src.domain.entities.clickup_space import ClickUpSpaceDTO
from backend.src.domain.entities.deployment import DeploymentDTO
from backend.src.domain.entities.git_repo import GitRepoDTO, GitRepoDetailDTO, RepoMemberDTO
from backend.src.domain.entities.member import MemberDTO, MemberWithReposDTO, RepoSummary
from backend.src.domain.exceptions.base.app_exception import AppException
from backend.src.infrastructure.handlers.exception_handler import FastAPIExceptionHandler
from backend.src.presentation.api import deps
from backend.src.presentation.api.routers import (
    auth_router,
    associator_router,
    clickup_router,
    deployment_router,
    generate_tasks_from_summary_router,
    member_router,
    repo_router,
    backlog_router,
    verification_tasks_router,
    clickup_task_save_router,
)


class _Container:
    """
    Simple container object for test dependency overrides.
    """

    def __init__(self) -> None:
        self.repo_service = MagicMock()
        self.member_service = MagicMock()
        self.clickup_service = MagicMock()
        self.associator_use_case = MagicMock()
        self.deployment_use_case = MagicMock()
        self.associator_service = self.associator_use_case
        self.deployment_service = self.deployment_use_case
        self.auth_use_case = MagicMock()
        self.backlog_use_case = MagicMock()
        self.save_task_use_case = MagicMock()
        self.generate_task_from_summary_use_case = MagicMock()
        self.verify_task_use_case = MagicMock()


@pytest.fixture
def container() -> _Container:
    """
    Provide a mocked service container.
    """
    return _Container()


@pytest.fixture
def app(container: _Container) -> FastAPI:
    """
    Create a FastAPI app with dependency overrides for tests.
    """
    app = FastAPI()
    app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
    app.include_router(clickup_router.router, prefix="/clickup", tags=["ClickUp"])
    app.include_router(associator_router.router, prefix="/associate", tags=["Associator"])
    app.include_router(repo_router.router, prefix="/repo", tags=["Repo"])
    app.include_router(member_router.router, prefix="/member", tags=["Member"])
    app.include_router(deployment_router.router, prefix="/deployment", tags=["Deployment"])
    app.include_router(backlog_router.router, prefix="/backlog", tags=["Backlog"])
    app.include_router(verification_tasks_router.router, prefix="/clickup", tags=["ClickUp"])
    app.include_router(generate_tasks_from_summary_router.router, prefix="/clickup", tags=["ClickUp"])
    app.include_router(clickup_task_save_router.router, prefix="/clickup", tags=["ClickUp"])

    app.add_exception_handler(AppException, FastAPIExceptionHandler.handle_app_exception)
    app.add_exception_handler(RequestValidationError, FastAPIExceptionHandler.handle_validation_exception)
    app.add_exception_handler(Exception, FastAPIExceptionHandler.handle_generic_exception)

    def override_get_container() -> Generator[_Container, None, None]:
        yield container

    app.dependency_overrides[deps.get_container] = override_get_container

    def override_get_backlog_use_case() -> MagicMock:
        return container.backlog_use_case

    app.dependency_overrides[deps.get_backlog_use_case] = override_get_backlog_use_case

    def override_get_save_task_use_case() -> MagicMock:
        return container.save_task_use_case

    app.dependency_overrides[deps.get_save_task_use_case] = override_get_save_task_use_case

    def override_get_generate_task_from_summary_use_case() -> MagicMock:
        return container.generate_task_from_summary_use_case

    app.dependency_overrides[deps.get_generate_task_from_summary_use_case] = override_get_generate_task_from_summary_use_case

    def override_get_verify_task_use_case() -> MagicMock:
        return container.verify_task_use_case

    app.dependency_overrides[deps.get_verify_task_use_case] = override_get_verify_task_use_case
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """
    Create a test client for the API.
    """
    return TestClient(app)


@pytest.fixture
def repo_dto() -> GitRepoDTO:
    """
    Sample repository DTO for tests.
    """
    return GitRepoDTO(id=1, name="repo-one", url="https://github.com/org/repo-one")


@pytest.fixture
def repo_detail_dto() -> GitRepoDetailDTO:
    """
    Sample repository detail DTO for tests.
    """
    return GitRepoDetailDTO(
        id=1,
        name="repo-one",
        url="https://github.com/org/repo-one",
        members=[RepoMemberDTO(id=10, username="alice", mail="alice@example.com")],
        clickup_space=None,
    )


@pytest.fixture
def member_dto() -> MemberDTO:
    """
    Sample member DTO for tests.
    """
    return MemberDTO(id=10, username="alice", mail="alice@example.com")


@pytest.fixture
def member_with_repos_dto() -> MemberWithReposDTO:
    """
    Sample member DTO with repos for tests.
    """
    return MemberWithReposDTO(
        id=10,
        username="alice",
        mail="alice@example.com",
        repos=[RepoSummary(id=1, name="repo-one", url="https://github.com/org/repo-one")],
    )


@pytest.fixture
def clickup_space_dto() -> ClickUpSpaceDTO:
    """
    Sample ClickUp space DTO for tests.
    """
    return ClickUpSpaceDTO(id=2, name="Platform", space_code="PLT")


@pytest.fixture
def deployment_dto() -> DeploymentDTO:
    """
    Sample deployment DTO for tests.
    """
    return DeploymentDTO(
        dep_id=42,
        environment="prod",
        ref="main",
        sha="abc1234",
        creator="octo",
        created_at=datetime(2024, 1, 1),
        description="release",
        state="success",
        log_url="https://example.com/log",
    )
