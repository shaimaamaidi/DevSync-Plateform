"""
Unit tests for MemberService.
"""

from unittest.mock import MagicMock

from backend.src.application.services.member_service import MemberService
from backend.src.domain.entities.member import MemberDTO, MemberUpdateDTO, MemberWithReposDTO


def test_update_member_calls_repository_update() -> None:
    """
    Test that updating a member calls the repository's update method and returns the correct DTO.
    """
    member_repo = MagicMock()
    member_repo.update.return_value = MemberWithReposDTO(id=1, username="alice", mail="a@b.com", repos=[])
    service = MemberService(member_repo)

    result = service.update_member(MemberUpdateDTO(id=1, username="alice"))

    member_repo.update.assert_called_once()
    assert result.id == 1


def test_get_member_by_mail_calls_repository_find() -> None:
    """
    Test that getting a member by mail calls the repository's find_by_mail method and returns the correct DTO.
    """
    member_repo = MagicMock()
    member_repo.find_by_mail.return_value = MemberWithReposDTO(id=2, username="bob", mail="b@c.com", repos=[])
    service = MemberService(member_repo)

    result = service.get_member_by_mail("b@c.com")

    member_repo.find_by_mail.assert_called_once_with("b@c.com")
    assert result.mail == "b@c.com"


def test_get_members_by_repo_calls_repository_find() -> None:
    """
    Test that getting members by repo calls the repository's find_by_repo_id method and returns the correct DTOs.
    """
    member_repo = MagicMock()
    member_repo.find_by_repo_id.return_value = [MemberDTO(id=3, username="eva", mail="e@d.com")]
    service = MemberService(member_repo)

    repo = MagicMock(id=99, url="https://example.com/repo")
    result = service.get_members_by_repo(repo)

    member_repo.find_by_repo_id.assert_called_once_with(99)
    assert len(result) == 1
