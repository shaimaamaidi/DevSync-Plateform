"""Dependency container for application services."""

import logging

from backend.src.application.services.member_service import MemberService
from backend.src.infrastructure.external.github_deployments import GitHubDeploymentAdapter
from backend.src.infrastructure.persistence.repositories.clickup_repository import SqlAlchemyClickUpRepository
from backend.src.infrastructure.persistence.repositories.repo_repository import SqlAlchemyRepoRepository
from backend.src.infrastructure.persistence.repositories.member_repository import SqlAlchemyMemberRepository
from backend.src.application.services.repo_service import RepoService
from backend.src.application.services.clickup_service import ClickUpService
from backend.src.application.services.associator_service import AssociatorService
from backend.src.application.services.deployment_service import DeploymentService


logger = logging.getLogger(__name__)


class Container:
    """Wire repositories, adapters, and services for a request."""
    def __init__(self, session):
        """Initialize dependencies using a shared session.

        Args:
            session: SQLAlchemy session.
        """
        logger.info("Initializing application container.")

        self.session = session

        try:
            # Repositories
            logger.info("Initializing repositories.")

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
                self.repo_service,
                self.clickup_service,
                self.member_service,
            )

            self.deployment_service = DeploymentService(self.github_service)

            logger.info("Application container initialized successfully.")

        except Exception as e:
            logger.error(
                "Failed to initialize application container: %s.",
                str(e),
            )
            raise