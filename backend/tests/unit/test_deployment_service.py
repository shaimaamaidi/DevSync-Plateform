"""
Unit tests for DeploymentService.
"""
from datetime import datetime

import pytest
from unittest.mock import MagicMock, AsyncMock

from backend.src.application.services.deployment_service import DeploymentService
from backend.src.domain.entities.deployment import DeploymentDTO


@pytest.mark.asyncio
async def test_list_deployments_delegates_to_github_service():
    """
    Test that listing deployments delegates to the GitHub service and returns the correct DTOs.
    """
    repo_url = "https://github.com/org/repo"
    repo_repo = MagicMock()
    repo_repo.find_by_url.return_value = MagicMock(url=repo_url)

    expected_deployments = [
        DeploymentDTO(
            dep_id=1,
            environment="prod",
            ref="main",
            sha="abc123",
            creator="octo",
            created_at=datetime(2024, 1, 1),
            description="release",
            state="success",
            log_url="https://example.com/log",
        )
    ]

    github_service = MagicMock()
    github_service.get_deployments = AsyncMock(return_value=expected_deployments)

    service = DeploymentService(repo_repo, github_service)

    result = await service.list_deployments(repo_url)

    repo_repo.find_by_url.assert_called_once_with(repo_url)
    github_service.get_deployments.assert_awaited_once_with(repo_url)

    assert result == expected_deployments