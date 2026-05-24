"""
GitHub dependency container for external infrastructure.

This module defines the BaseGitHubContainer class, which is responsible for
initializing and exposing GitHub-related infrastructure components such as
deployment and CI/CD-related services.

It acts as a dedicated dependency container for GitHub integrations used
across the application.

Classes:
    BaseGitHubContainer: Container for GitHub external dependencies.
"""

import logging
from backend.src.domain.exceptions.base.app_exception import AppException
from backend.src.infrastructure.external.github.github_deployments import GitHubDeploymentAdapter


logger = logging.getLogger(__name__)


class BaseGitHubContainer:
    """
    GitHub dependency container.

    This container is responsible for initializing and managing GitHub-related
    infrastructure components required by the application.

    It currently provides:
    - GitHub deployment service adapter for retrieving deployment information

    This container ensures centralized initialization of GitHub integrations
    and consistent error handling for external service availability.
    """

    def __init__(self):
        """
        Initialize GitHub infrastructure dependencies.

        This constructor initializes the GitHub deployment adapter used to
        interact with GitHub deployment-related APIs.

        Raises:
            AppException: If GitHub infrastructure initialization fails,
            indicating that GitHub services are currently unavailable.
        """
        try:
            self.github_deployment_service = GitHubDeploymentAdapter()
        except Exception as e:
            logger.exception("Failed to initialize GitHubDeploymentAdapter.")
            raise AppException(
                "GitHub services are currently unavailable. Please try again later.",
                "GITHUB_ADAPTER_INIT_ERROR",
                http_status=500,
            ) from e