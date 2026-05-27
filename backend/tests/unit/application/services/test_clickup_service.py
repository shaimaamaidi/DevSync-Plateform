"""
Unit tests for ClickUpService.
"""

from unittest.mock import MagicMock

from backend.src.application.services.clickup_service import ClickUpService
from backend.src.domain.entities.clickup_space import ClickUpSpaceCreateDTO, ClickUpSpaceDTO


def test_add_space_calls_repository_save() -> None:
    """
    Test that adding a ClickUp space calls the repository's save method and returns the correct DTO.
    """
    repo = MagicMock()
    repo.save.return_value = ClickUpSpaceDTO(id=1, name="Platform", space_code="PLT")
    service = ClickUpService(repo)

    result = service.add_space(ClickUpSpaceCreateDTO(name="Platform", space_code="PLT"))

    repo.save.assert_called_once()
    assert result.space_code == "PLT"
