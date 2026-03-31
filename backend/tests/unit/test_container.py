"""Unit tests for Container dependency injection."""

from unittest.mock import MagicMock
from backend.src.infrastructure.di.container import Container

def test_container_initializes_services():
    session = MagicMock()
    container = Container(session)
    assert container.auth_service is not None
    assert container.member_service is not None
    assert container.repo_service is not None
    assert container.clickup_service is not None
    assert container.associator_service is not None
    assert container.deployment_service is not None
    assert container.github_service is not None
