"""
Unit tests for SqlAlchemyMemberRepository.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from backend.src.domain.entities.member import MemberCreateDTO, MemberUpdateDTO, RepoRefDTO
from backend.src.domain.exceptions.common.invalid_input_exception import InvalidInputException
from backend.src.domain.exceptions.member.member_not_found_exception import MemberNotFoundException
from backend.src.domain.exceptions.member.member_persistence_exception import MemberPersistenceException
from backend.src.infrastructure.persistence.repositories.member_repository import SqlAlchemyMemberRepository


def test_member_find_credentials_requires_mail() -> None:
    """
    find_credentials_by_mail should require non-empty mail.
    """
    repo = SqlAlchemyMemberRepository(MagicMock())

    with pytest.raises(InvalidInputException):
        repo.find_credentials_by_mail("")


def test_member_save_requires_fields() -> None:
    """
    save should raise InvalidInputException when fields missing.
    """
    repo = SqlAlchemyMemberRepository(MagicMock())

    with pytest.raises(InvalidInputException):
        repo.save(MemberCreateDTO(username=None, mail=None, password=None))


def test_member_find_by_id_not_found() -> None:
    """
    find_by_id should raise MemberNotFoundException when no record.
    """
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.return_value = None
    repo = SqlAlchemyMemberRepository(session)

    with pytest.raises(MemberNotFoundException):
        repo.find_by_id(99)


def test_member_find_all_with_repos_wraps_sqlalchemy_error() -> None:
    """
    find_all_with_repos should wrap SQLAlchemyError into MemberPersistenceException.
    """
    session = MagicMock()
    session.query.return_value.all.side_effect = SQLAlchemyError("fail")
    repo = SqlAlchemyMemberRepository(session)

    with pytest.raises(MemberPersistenceException):
        repo.find_all_with_repos()


def test_member_update_happy_path() -> None:
    """
    update should commit and return member with repos DTO.
    """
    model = SimpleNamespace(
        id=1,
        username="old",
        arabic_name="old",
        mail="a@b.com",
        password="hash",
        repos=[],
    )
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.return_value = model

    repo = SqlAlchemyMemberRepository(session)
    result = repo.update(MemberUpdateDTO(id=1, username="new"))

    assert result.id == 1
    assert result.username == "new"
    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(model)


def test_member_delete_happy_path() -> None:
    """
    delete should remove record and commit.
    """
    model = SimpleNamespace(id=3)
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.return_value = model

    repo = SqlAlchemyMemberRepository(session)
    result = repo.delete(3)

    assert result is True
    session.delete.assert_called_once_with(model)
    session.commit.assert_called_once()


def test_member_update_repos_by_id() -> None:
    """
    update should associate repos when ids exist.
    """
    repo_model = SimpleNamespace(id=7, name="repo", url="https://example.com/repo")
    member_model = SimpleNamespace(
        id=1,
        username="old",
        arabic_name="old",
        mail="a@b.com",
        password="hash",
        repos=[],
    )
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.return_value = member_model
    session.query.return_value.filter.return_value.all.return_value = [repo_model]

    repo = SqlAlchemyMemberRepository(session)
    result = repo.update(MemberUpdateDTO(id=1, repos=[RepoRefDTO(id=7)]))

    assert result.id == 1
    assert member_model.repos[0].id == 7
    session.commit.assert_called_once()


def test_member_update_repos_by_url() -> None:
    """
    update should associate repos when urls exist.
    """
    repo_model = SimpleNamespace(id=7, name="repo", url="https://example.com/repo")
    member_model = SimpleNamespace(
        id=1,
        username="old",
        arabic_name="old",
        mail="a@b.com",
        password="hash",
        repos=[],
    )
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.return_value = member_model
    session.query.return_value.filter.return_value.all.return_value = [repo_model]

    repo = SqlAlchemyMemberRepository(session)
    result = repo.update(MemberUpdateDTO(id=1, repos=[RepoRefDTO(url="https://example.com/repo")]))

    assert result.id == 1
    assert member_model.repos[0].url == "https://example.com/repo"
    session.commit.assert_called_once()


def test_member_update_repos_missing_raises() -> None:
    """
    update should raise InvalidInputException when repos not found.
    """
    member_model = SimpleNamespace(
        id=1,
        username="old",
        arabic_name="old",
        mail="a@b.com",
        password="hash",
        repos=[],
    )
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.return_value = member_model
    session.query.return_value.filter.return_value.all.return_value = []

    repo = SqlAlchemyMemberRepository(session)

    with pytest.raises(InvalidInputException):
        repo.update(MemberUpdateDTO(id=1, repos=[RepoRefDTO(id=999)]))


def test_member_update_repos_mixed_id_and_url() -> None:
    """
    update should associate repos when mixed id/url references exist.
    """
    repo_by_id = SimpleNamespace(id=7, name="repo1", url="https://example.com/repo1")
    repo_by_url = SimpleNamespace(id=8, name="repo2", url="https://example.com/repo2")
    member_model = SimpleNamespace(
        id=1,
        username="old",
        arabic_name="old",
        mail="a@b.com",
        password="hash",
        repos=[],
    )
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.return_value = member_model
    session.query.return_value.filter.return_value.all.return_value = [repo_by_id, repo_by_url]

    repo = SqlAlchemyMemberRepository(session)
    result = repo.update(
        MemberUpdateDTO(
            id=1,
            repos=[RepoRefDTO(id=7), RepoRefDTO(url="https://example.com/repo2")],
        )
    )

    assert result.id == 1
    assert {r.id for r in member_model.repos} == {7, 8}
    session.commit.assert_called_once()


def test_member_update_repos_requires_id_or_url() -> None:
    """
    update should raise InvalidInputException when repos lack id/url.
    """
    member_model = SimpleNamespace(
        id=1,
        username="old",
        arabic_name="old",
        mail="a@b.com",
        password="hash",
        repos=[],
    )
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.return_value = member_model

    repo = SqlAlchemyMemberRepository(session)

    with pytest.raises(InvalidInputException):
        repo.update(MemberUpdateDTO(id=1, repos=[RepoRefDTO()]))
