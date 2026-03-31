"""
Dependency container for application services.

This module defines the Container class, which wires together repositories, adapters, and application services for dependency injection in the application layer.

Classes:
    Container: Dependency injection container for repositories, adapters, and services.
"""

import logging

from backend.src.application.services.auth_service import AuthService
from backend.src.application.services.member_service import MemberService
from backend.src.domain.exceptions.app_exception import AppException
from backend.src.infrastructure.external.github_deployments import GitHubDeploymentAdapter
from backend.src.infrastructure.persistence.repositories.clickup_repository import SqlAlchemyClickUpRepository
from backend.src.infrastructure.persistence.repositories.refresh_token_repository import SqlAlchemyRefreshTokenRepository
from backend.src.infrastructure.persistence.repositories.repo_repository import SqlAlchemyRepoRepository
from backend.src.infrastructure.persistence.repositories.member_repository import SqlAlchemyMemberRepository
from backend.src.application.services.repo_service import RepoService
from backend.src.application.services.clickup_service import ClickUpService
from backend.src.application.services.associator_service import AssociatorService
from backend.src.application.services.deployment_service import DeploymentService
from backend.src.infrastructure.security.jwt_handler import JWTHandler

logger = logging.getLogger(__name__)


class Container:
    """
    Dependency injection container for repositories, adapters, and services.

    Attributes:
        session: SQLAlchemy session used for repository instantiation.
        jwt_handler (JWTHandler): JWT handler for authentication.
        refresh_token_repo (SqlAlchemyRefreshTokenRepository): Refresh token repository.
        repo_repo (SqlAlchemyRepoRepository): Repository for Git repositories.
        member_repo (SqlAlchemyMemberRepository): Repository for members.
        clickup_repo (SqlAlchemyClickUpRepository): Repository for ClickUp spaces.
        github_service (GitHubDeploymentAdapter): Adapter for GitHub deployments.
        repo_service (RepoService): Application service for repositories.
        member_service (MemberService): Application service for members.
        clickup_service (ClickUpService): Application service for ClickUp.
        associator_service (AssociatorService): Application service for associating repos, members, and ClickUp.
        auth_service (AuthService): Application service for authentication.
        deployment_service (DeploymentService): Application service for deployments.
    """
    def __init__(self, session):
        """
        Initialize dependencies using a shared session.

        Args:
            session (Session): SQLAlchemy session used for repository instantiation.

        Raises:
            AppException: If container initialization fails.
        """
        logger.info("Initializing application container.")

        self.session = session

        try:
            # Technical Service
            self.jwt_handler = JWTHandler()

            # Repositories
            logger.info("Initializing repositories.")

            self.refresh_token_repo = SqlAlchemyRefreshTokenRepository(self.session)
            self.repo_repo = SqlAlchemyRepoRepository(self.session)
            self.member_repo = SqlAlchemyMemberRepository(self.session)
            self.clickup_repo = SqlAlchemyClickUpRepository(self.session)

            # External services
            logger.info("Initializing external services.")

            self.github_service = GitHubDeploymentAdapter()

            # Application services
            logger.info("Initializing application services.")

            self.repo_service = RepoService(self.repo_repo)
            self.member_service = MemberService(self.member_repo)
            self.clickup_service = ClickUpService(self.clickup_repo)

            self.associator_service = AssociatorService(
                self.repo_repo,
                self.clickup_repo,
                self.member_repo,
            )

            self.auth_service = AuthService(
                member_repository=self.member_repo,
                jwt_handler=self.jwt_handler,
                refresh_token_repository=self.refresh_token_repo,
            )

            self.deployment_service = DeploymentService(self.github_service)

            logger.info("Application container initialized successfully.")

        except Exception as e:
            logger.exception("Failed to initialize application container.")
            raise AppException("CONTAINER_INIT_ERROR", "Failed to initialize container") from e