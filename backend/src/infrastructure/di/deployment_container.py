"""
Dependency container for deployment and task status workflow.

This module defines the DeploymentContainer class, which is responsible for
wiring together GitHub-related infrastructure and exposing factory methods
for deployment tracking and task status use cases.

It acts as an application-scoped dependency injection container for:
- GitHub deployment services
- Task status workflow orchestration
- Deployment-related use case factories

Classes:
    DeploymentContainer: Application-scoped DI container for deployment
    and task status use cases.
"""

import logging

from backend.src.application.use_cases.deployment_use_case import DeploymentUseCase
from backend.src.domain.exceptions.base.app_exception import AppException
from backend.src.domain.ports.repositories.i_repo_repository import IRepoRepository
from backend.src.infrastructure.di.base_github_container import BaseGitHubContainer


logger = logging.getLogger(__name__)


class DeploymentContainer(BaseGitHubContainer):
    """
    Dependency injection container for deployment tracking and task status workflows.

    This container extends BaseGitHubContainer and provides access to GitHub
    deployment infrastructure while exposing factories for domain use cases.

    It is responsible for:
    - Initializing GitHub deployment infrastructure (via BaseGitHubContainer)
    - Providing deployment-related use case factories
    - Acting as a bridge between infrastructure and application layers

    Attributes:
        github_deployment_service (GitHubDeploymentAdapter):
            Service responsible for retrieving deployment information from GitHub.
    """

    def __init__(self):
        """
        Initialize the DeploymentContainer.

        This constructor initializes the base GitHub infrastructure and ensures
        all deployment-related services are ready for use.

        Raises:
            AppException: If GitHub or deployment infrastructure initialization fails.
        """
        logger.info("Initializing deployment container.")

        try:
            super().__init__()
            logger.info("Deployment container initialized successfully.")

        except AppException:
            raise
        except Exception as e:
            logger.exception("Failed to initialize deployment container.")
            raise AppException(
                "Deployment services are currently unavailable. Please try again later.",
                "DEPLOYMENT_CONTAINER_INIT_ERROR",
                http_status=500,
            ) from e

    def create_deployment_use_case(self, github_repository: IRepoRepository) -> DeploymentUseCase:
        """
        Factory method for DeploymentUseCase.

        This method creates a fully initialized DeploymentUseCase by combining:
        - GitHub deployment infrastructure service
        - Repository abstraction for GitHub repositories

        Args:
            github_repository: Request-scoped repository used to access GitHub repo data.

        Returns:
            DeploymentUseCase: Fully initialized use case for deployment tracking.
        """
        return DeploymentUseCase(
            github_repository,
            self.github_deployment_service,
        )