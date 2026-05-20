"""
Unit tests for ClickUp structure use cases.
"""

from unittest.mock import MagicMock

from backend.src.application.use_cases.clickup_structure_management_use_case import ClickUpStructureCreationUseCase
from backend.src.application.use_cases.clickup_structure_metadata_use_case import ClickUpStructureMetadataUseCase
from backend.src.domain.entities.clickup.add_status_request import AddStatusRequest
from backend.src.domain.entities.clickup.create_folder_request import CreateFolderRequest
from backend.src.domain.entities.clickup.create_list_request import CreateListRequest
from backend.src.domain.entities.clickup.create_space_request import CreateSpaceRequest
from backend.src.domain.entities.clickup.folder_with_list_metadata import FolderWithListsMetadata
from backend.src.domain.entities.clickup.list_metadata import ClickUpListMetadata
from backend.src.domain.entities.clickup.status import ClickUpStatus, StatusType
from backend.src.domain.entities.clickup_space import ClickUpSpaceCreateDTO, ClickUpSpaceDTO


def test_create_space_delegates_to_writer_and_service() -> None:
    clickup_service = MagicMock()
    clickup_service.add_space.return_value = ClickUpSpaceDTO(id=1, name="Platform", space_code="PLT")
    clickup_writer = MagicMock()
    clickup_writer.create_space.return_value = ("PLT", "Platform")

    use_case = ClickUpStructureCreationUseCase(clickup_service=clickup_service, clickup_writer=clickup_writer)

    result = use_case.create_space(CreateSpaceRequest(space_id="space-1"))

    clickup_writer.create_space.assert_called_once_with("space-1")
    clickup_service.add_space.assert_called_once_with(ClickUpSpaceCreateDTO(name="Platform", space_code="PLT"))
    assert result.space_code == "PLT"


def test_create_folder_returns_empty_lists_metadata() -> None:
    clickup_service = MagicMock()
    clickup_writer = MagicMock()
    clickup_writer.create_folder.return_value = ("folder-1", "Backend")

    use_case = ClickUpStructureCreationUseCase(clickup_service=clickup_service, clickup_writer=clickup_writer)

    result = use_case.create_folder(CreateFolderRequest(space_id="space-1", name="Backend"))

    clickup_writer.create_folder.assert_called_once_with("space-1", "Backend")
    assert result == FolderWithListsMetadata(id="folder-1", name="Backend", lists=[])


def test_create_list_delegates_to_writer() -> None:
    clickup_service = MagicMock()
    clickup_writer = MagicMock()
    expected = ClickUpListMetadata(id="list-1", name="Sprint", statuses=["To Do"], priorities=["High"])
    clickup_writer.create_list.return_value = expected

    use_case = ClickUpStructureCreationUseCase(clickup_service=clickup_service, clickup_writer=clickup_writer)

    result = use_case.create_list(CreateListRequest(space_id="space-1", name="Sprint", folder_id="folder-1"))

    clickup_writer.create_list.assert_called_once_with("space-1", "Sprint", "folder-1")
    assert result is expected


def test_add_status_builds_clickup_status_and_delegates() -> None:
    clickup_service = MagicMock()
    clickup_writer = MagicMock()
    expected = ClickUpListMetadata(id="list-1", name="Sprint", statuses=["Review"], priorities=[])
    clickup_writer.add_status_to_list.return_value = expected

    use_case = ClickUpStructureCreationUseCase(clickup_service=clickup_service, clickup_writer=clickup_writer)
    request = AddStatusRequest(list_id="list-1", status="Review", color="#ff0000", type=StatusType.CUSTOM)

    result = use_case.add_status(request)

    clickup_writer.add_status_to_list.assert_called_once()
    called_list_id, called_status = clickup_writer.add_status_to_list.call_args.args
    assert called_list_id == "list-1"
    assert called_status == ClickUpStatus(status="Review", color="#ff0000", type=StatusType.CUSTOM)
    assert called_status.to_dict() == {"status": "Review", "color": "#ff0000", "type": "custom"}
    assert result is expected


def test_get_space_structure_metadata_delegates() -> None:
    clickup_reader = MagicMock()
    expected = [FolderWithListsMetadata(id="folder-1", name="Backend", lists=[])]
    clickup_reader.get_space_structure_metadata.return_value = expected

    use_case = ClickUpStructureMetadataUseCase(clickup_reader=clickup_reader)

    result = use_case.get_space_structure_metadata("space-1")

    clickup_reader.get_space_structure_metadata.assert_called_once_with("space-1")
    assert result is expected