"""
Integration test for the /deployments endpoint.
"""

from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from backend.src.domain.entities.deployment import DeploymentDTO


def test_get_deployments_endpoint_returns_expected_data(client: TestClient, container):
    """
    Ensure the /deployments endpoint returns the list of deployments
    from the DeploymentService for a given repo URL.
    """
    repo_url = "https://github.com/org/repo"
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

    container.deployment_use_case.list_deployments = AsyncMock(return_value=expected_deployments)

    response = client.get(f"/deployment/list?repo_url={repo_url}")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == len(expected_deployments)
    assert data[0]["dep_id"] == expected_deployments[0].dep_id
    assert data[0]["environment"] == expected_deployments[0].environment

    container.deployment_use_case.list_deployments.assert_awaited_once_with(repo_url)