"""Unit tests for DeploymentService."""

from unittest.mock import MagicMock

from backend.src.application.services.deployment_service import DeploymentService
from backend.src.domain.entities.deployment import DeploymentDTO


def test_list_deployments_delegates_to_github_service() -> None:
    github_service = MagicMock()
    github_service.get_deployments.return_value = [
        DeploymentDTO(
            dep_id=1,
            environment="prod",
            ref="main",
            sha="abc123",
            creator="octo",
            created_at="2024-01-01",
            description="release",
            state="success",
            log_url="https://example.com/log",
        )
    ]
    service = DeploymentService(github_service)

    result = service.list_deployments("https://github.com/org/repo")

    github_service.get_deployments.assert_called_once_with("https://github.com/org/repo")
    assert result[0].dep_id == 1
