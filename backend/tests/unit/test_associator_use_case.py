"""Unit tests for AssociatorUseCase."""

from unittest.mock import MagicMock

import pytest

from backend.src.application.use_cases.associator_use_case import AssociatorUseCase
from backend.src.domain.entities.associator import AssociateClickUpSpaceRequest, RepoMembersRequest, MemberMailDTO
from backend.src.domain.entities.clickup_space import ClickUpSpaceDTO
from backend.src.domain.entities.git_repo import GitRepoDTO, GitRepoDetailDTO, RepoMemberDTO
from backend.src.domain.entities.member import MemberWithReposDTO
from backend.src.domain.exceptions.member.invalid_member_data_exception import InvalidMemberDataException


def test_associate_clickup_space_updates_repo() -> None:
    """
    Test that associating a ClickUp space updates the repository and returns the correct response DTO.
    """
    repo_service = MagicMock()
    clickup_service = MagicMock()
    member_service = MagicMock()

    clickup_service.find_by_space_code.return_value = ClickUpSpaceDTO(id=2, name="Platform", space_code="PLT")
    repo_service.find_by_url.return_value = GitRepoDTO(id=1, name="repo", url="https://github.com/org/repo")
    repo_service.find_by_id.return_value = GitRepoDetailDTO(
        id=1,
        name="repo",
        url="https://github.com/org/repo",
        members=[],
        clickup_space=None,
    )
    repo_service.update.return_value = GitRepoDetailDTO(
        id=1,
        name="repo",
        url="https://github.com/org/repo",
        members=[],
        clickup_space=None,
    )

    use_case = AssociatorUseCase(repo_service, clickup_service, member_service)

    result = use_case.associate_clickup_space(
        AssociateClickUpSpaceRequest(repo_url="https://github.com/org/repo", space_code="PLT")
    )

    repo_service.update.assert_called_once()
    assert result.clickup_space.space_code == "PLT"


def test_add_members_requires_mail() -> None:
    """
    Test that adding a member without an email raises InvalidMemberDataException.
    """
    repo_service = MagicMock()
    clickup_service = MagicMock()
    member_service = MagicMock()
    repo_service.update.return_value = GitRepoDetailDTO(
        id=1,
        name="repo",
        url="https://github.com/org/repo",
        members=[],
        clickup_space=None,
    )
    use_case = AssociatorUseCase(repo_service, clickup_service, member_service)

    request = RepoMembersRequest(repo_url="https://github.com/org/repo", members=[MemberMailDTO(mail=None)])

    with pytest.raises(InvalidMemberDataException):
        use_case.add_members(request)


def test_remove_members_builds_payload() -> None:
    """Test that removing members builds the correct payload and updates the repository."""
    repo_service = MagicMock()
    clickup_service = MagicMock()
    member_service = MagicMock()

    repo_service.find_by_url.return_value = GitRepoDTO(id=1, name="repo", url="https://github.com/org/repo")
    repo_service.find_by_id.return_value = GitRepoDetailDTO(
        id=1,
        name="repo",
        url="https://github.com/org/repo",
        members=[RepoMemberDTO(id=1, username="alice", mail="alice@example.com")],
        clickup_space=None,
    )
    member_service.get_member_by_mail.return_value = MemberWithReposDTO(
        id=2,
        username="bob",
        mail="bob@example.com",
        repos=[],
    )
    repo_service.update.return_value = GitRepoDetailDTO(
        id=1,
        name="repo",
        url="https://github.com/org/repo",
        members=[],
        clickup_space=None,
    )

    use_case = AssociatorUseCase(repo_service, clickup_service, member_service)

    request = RepoMembersRequest(
        repo_url="https://github.com/org/repo",
        members=[MemberMailDTO(mail="bob@example.com")],
    )

    result = use_case.remove_members(request)

    repo_service.update.assert_called_once()
    assert result.repo.id == 1
