"""
Unit tests for ClickUpWorkSpaceWriter.

Cover create/delete space, create folder/list, add status, invite/remove members,
and error message extraction.
"""

from types import SimpleNamespace

import pytest

from backend.src.infrastructure.external.clickup.writer.clickup_workspace_writer import ClickUpWorkSpaceWriter
from backend.src.domain.entities.clickup.status import ClickUpStatus
from backend.src.domain.entities.clickup.list_metadata import ClickUpListMetadata
from backend.src.domain.entities.clickup.member_invitation import ClickUpMemberInvitation
from backend.src.domain.exceptions.clickup.clickup_write_exception import ClickUpWriteException


class DummyResp:
    def __init__(self, status_code=200, payload=None, text="ok"):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self):
        return self._payload


def test_create_and_delete_space_success_and_failure() -> None:
    http = SimpleNamespace(team_id="team-1")
    http.post_raw = lambda endpoint, payload: DummyResp(status_code=200, payload={"id": "s1", "name": payload["name"]})
    writer = ClickUpWorkSpaceWriter(http)

    sid, name = writer.create_space("NewSpace")
    assert sid == "s1"
    assert name == "NewSpace"

    http.delete_raw = lambda endpoint: DummyResp(status_code=200)
    assert writer.delete_space("s1") is True

    http_fail = SimpleNamespace(team_id="team-1")
    http_fail.post_raw = lambda endpoint, payload: DummyResp(status_code=500, payload={"err": "boom"}, text="boom")
    writer_fail = ClickUpWorkSpaceWriter(http_fail)

    with pytest.raises(ClickUpWriteException):
        writer_fail.create_space("FailSpace")

    http_fail.delete_raw = lambda endpoint: DummyResp(status_code=500, payload={"err": "gone"}, text="gone")
    with pytest.raises(ClickUpWriteException):
        writer_fail.delete_space("s1")


def test_create_folder_and_list_success_and_failure() -> None:
    http = SimpleNamespace()
    http.post_raw = lambda endpoint, payload: DummyResp(status_code=200, payload={"id": "f1", "name": payload["name"]})
    writer = ClickUpWorkSpaceWriter(http)

    fid, fname = writer.create_folder("space-1", "FolderA")
    assert fid == "f1" and fname == "FolderA"

    http.post_raw = lambda endpoint, payload: DummyResp(status_code=200, payload={"id": "l1", "name": payload["name"], "statuses": [{"status": "todo"}], "features": {"priorities": {"priorities": [{"priority": "low"}]}}})
    lm = writer.create_list("space-1", name="ListX")
    assert isinstance(lm, ClickUpListMetadata)
    assert lm.id == "l1"

    http_fail = SimpleNamespace()
    http_fail.post_raw = lambda endpoint, payload: DummyResp(status_code=500, payload={"err": "bad"}, text="bad")
    writer_fail = ClickUpWorkSpaceWriter(http_fail)

    with pytest.raises(ClickUpWriteException):
        writer_fail.create_folder("space-1", "F")

    with pytest.raises(ClickUpWriteException):
        writer_fail.create_list("space-1", name="L")


def test_add_status_to_list_appends_and_puts(monkeypatch) -> None:
    http = SimpleNamespace()
    http.get = lambda endpoint: {"id": "l1", "name": "List1", "statuses": [{"status": "todo"}]}

    http.put_raw = lambda endpoint, payload: DummyResp(status_code=200, payload={"id": "l1", "name": "List1", "statuses": [{"status": "todo"}, {"status": "inprogress"}], "features": {"priorities": {"priorities": [{"priority": "low"}]}}})

    writer = ClickUpWorkSpaceWriter(http)

    from backend.src.domain.entities.clickup.status import StatusType

    status = ClickUpStatus(status="inprogress", color="#fff", type=StatusType.CUSTOM)
    lm = writer.add_status_to_list("l1", status)

    assert isinstance(lm, ClickUpListMetadata)
    assert "inprogress" in lm.statuses

    http_fail = SimpleNamespace()
    http_fail.get = lambda endpoint: {"id": "l1", "name": "List1", "statuses": []}
    http_fail.put_raw = lambda endpoint, payload: DummyResp(status_code=500, payload={"err": "x"}, text="x")
    writer_fail = ClickUpWorkSpaceWriter(http_fail)

    with pytest.raises(ClickUpWriteException):
        writer_fail.add_status_to_list("l1", status)


def test_workspace_member_invite_and_remove() -> None:
    http = SimpleNamespace(team_id="t1")
    http.post_raw = lambda endpoint, payload: DummyResp(status_code=200)
    writer = ClickUpWorkSpaceWriter(http)

    from backend.src.domain.entities.clickup.member_invitation import ClickUpMemberRole

    invite = ClickUpMemberInvitation(email="a@x.com", role=ClickUpMemberRole.ADMIN)
    assert writer.add_workspace_member(invite) is True

    http.delete_raw = lambda endpoint: DummyResp(status_code=200)
    assert writer.remove_workspace_member(123) is True

    http_fail = SimpleNamespace(team_id="t1")
    http_fail.post_raw = lambda endpoint, payload: DummyResp(status_code=500, payload={"err": "e"}, text="e")
    writer_fail = ClickUpWorkSpaceWriter(http_fail)

    with pytest.raises(ClickUpWriteException):
        writer_fail.add_workspace_member(invite)

    http_fail.delete_raw = lambda endpoint: DummyResp(status_code=500, payload={"err": "e"}, text="e")
    with pytest.raises(ClickUpWriteException):
        writer_fail.remove_workspace_member(123)


def test_get_error_message_prefers_json_err() -> None:
    class FakeResp:
        def __init__(self, text, payload):
            self.text = text
            self._payload = payload

        def json(self):
            return self._payload

    resp = FakeResp("plain", {"err": "jsonerr"})
    assert ClickUpWorkSpaceWriter._get_error_message(resp) == "jsonerr"
