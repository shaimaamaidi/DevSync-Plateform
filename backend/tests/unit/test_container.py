"""
Unit tests for Container dependency injection.
"""

from unittest.mock import MagicMock, patch
from backend.src.infrastructure.di.container import Container

def test_container_initializes_services():
    """
    Test that the Container initializes all services and repositories correctly with mocked dependencies.
    """
    session = MagicMock()
    with patch("backend.src.application.services.auth_service.AuthService"), \
        patch("backend.src.application.services.member_service.MemberService"), \
        patch("backend.src.application.services.repo_service.RepoService"), \
        patch("backend.src.application.services.clickup_service.ClickUpService"), \
        patch("backend.src.application.services.associator_service.AssociatorService"), \
        patch("backend.src.application.services.deployment_service.DeploymentService"), \
        patch("backend.src.infrastructure.external.github_deployments.GitHubDeploymentAdapter"), \
        patch("backend.src.infrastructure.di.container.JWTHandler"), \
        patch("backend.src.infrastructure.persistence.repositories.clickup_repository.SqlAlchemyClickUpRepository"), \
        patch("backend.src.infrastructure.persistence.repositories.refresh_token_repository.SqlAlchemyRefreshTokenRepository"), \
        patch("backend.src.infrastructure.persistence.repositories.repo_repository.SqlAlchemyRepoRepository"), \
        patch("backend.src.infrastructure.persistence.repositories.member_repository.SqlAlchemyMemberRepository"):
        container = Container(session)
        assert container.auth_service is not None
        assert container.member_service is not None
        assert container.repo_service is not None
        assert container.clickup_service is not None
        assert container.associator_service is not None
        assert container.deployment_service is not None
        assert container.github_service is not None