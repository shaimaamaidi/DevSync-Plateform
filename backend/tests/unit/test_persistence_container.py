"""
Unit tests for Container dependency injection.
"""

from unittest.mock import MagicMock, patch

from backend.src.infrastructure.di.persistence_container import PersistenceContainer


def test_container_initializes_services() -> None:
    """
    Test that the Container initializes repositories, use cases, and services.
    """
    session = MagicMock()
    with patch("backend.src.infrastructure.persistence.repositories.clickup_repository.SqlAlchemyClickUpRepository"), \
        patch("backend.src.infrastructure.persistence.repositories.refresh_token_repository.SqlAlchemyRefreshTokenRepository"), \
        patch("backend.src.infrastructure.persistence.repositories.repo_repository.SqlAlchemyRepoRepository"), \
        patch("backend.src.infrastructure.persistence.repositories.member_repository.SqlAlchemyMemberRepository"), \
        patch("backend.src.infrastructure.security.jwt_handler.JWTHandler"), \
        patch("backend.src.infrastructure.external.github.github_deployments.GitHubDeploymentAdapter"):
        container = PersistenceContainer(session)

        assert container.refresh_token_repo is not None
        assert container.repo_repo is not None
        assert container.member_repo is not None
        assert container.clickup_repo is not None
        assert container.jwt_handler is not None
        assert container.associator_use_case is not None
        assert container.auth_use_case is not None
        assert container.repo_service is not None
        assert container.member_service is not None
        assert container.clickup_service is not None