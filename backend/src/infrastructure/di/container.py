"""
Dependency container for application services.

This module defines the Container class, which wires together repositories,
technical services, external adapters, and application services for dependency
injection within the application layer.

Classes:
    Container: Request-scoped dependency injection container.
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
    Request-scoped dependency injection container.

    This container is responsible for initializing and wiring all dependencies
    required for handling application use cases, including repositories,
    technical services, external adapters, and application services.

    Attributes:
        session: SQLAlchemy session used for repository instantiation.

        # Repositories
        refresh_token_repo (SqlAlchemyRefreshTokenRepository)
        repo_repo (SqlAlchemyRepoRepository)
        member_repo (SqlAlchemyMemberRepository)
        clickup_repo (SqlAlchemyClickUpRepository)

        # Technical services
        jwt_handler (JWTHandler)

        # External services
        github_service (GitHubDeploymentAdapter)

        # Application services
        repo_service (RepoService)
        member_service (MemberService)
        clickup_service (ClickUpService)
        associator_service (AssociatorService)
        auth_service (AuthService)
        deployment_service (DeploymentService)
    """

    def __init__(self, session):
        """
        Initialize container dependencies using a shared session.

        Args:
            session (Session): SQLAlchemy session used for repository instantiation.

        Raises:
            AppException: If container initialization fails.
        """
        logger.info("Initializing request container.")

        self.session = session

        try:
            self._init_repositories()
            self._init_technical_services()
            self._init_external_services()
            self._init_application_services()

            logger.info("Request container initialized successfully.")

        except Exception as e:
            logger.exception("Failed to initialize request container.")
            raise AppException( "Failed to initialize container.", "CONTAINER_INIT_ERROR") from e

    # Repositories
    def _init_repositories(self):
        """
        Initialize persistence repositories.

        This method instantiates all database repositories using the shared session.
        """
        logger.info("Initializing repositories.")

        self.refresh_token_repo = SqlAlchemyRefreshTokenRepository(self.session)
        self.repo_repo = SqlAlchemyRepoRepository(self.session)
        self.member_repo = SqlAlchemyMemberRepository(self.session)
        self.clickup_repo = SqlAlchemyClickUpRepository(self.session)

    # Technical services
    def _init_technical_services(self):
        """
        Initialize technical services.

        This includes infrastructure-level utilities such as JWT handling.
        """
        self.jwt_handler = JWTHandler(self.member_repo)

    # External services
    def _init_external_services(self):
        """
        Initialize external service adapters.

        This includes integrations with third-party systems such as GitHub.
        """
        logger.info("Initializing external services.")

        self.github_service = GitHubDeploymentAdapter()

    # Application services
    def _init_application_services(self):
        """
        Initialize application services.

        This method wires repositories and external services into business-level
        application services.
        """
        logger.info("Initializing application services.")

        self.repo_service = RepoService(self.repo_repo)
        self.member_service = MemberService(self.member_repo)
        self.clickup_service = ClickUpService(self.clickup_repo)

        self.associator_service = AssociatorService(
            repo_service=self.repo_repo,
            clickup_service=self.clickup_repo,
            member_service=self.member_repo,
        )

        self.auth_service = AuthService(
            member_repository=self.member_repo,
            jwt_handler=self.jwt_handler,
            refresh_token_repository=self.refresh_token_repo,
        )

        self.deployment_service = DeploymentService(self.repo_repo, self.github_service)