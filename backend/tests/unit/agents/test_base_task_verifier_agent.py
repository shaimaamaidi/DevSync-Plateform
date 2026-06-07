from types import SimpleNamespace

from backend.src.infrastructure.external.task_verification.base_task_verifier_agent import (
    BaseTaskVerifierAgent,
)


class _DummyVerifier(BaseTaskVerifierAgent):
    def __init__(self):
        super().__init__(prompt_loader=object(), agent_name="d", folder_name="f", prompt_name="p", response_format=dict)

    def _serialize_generated(self, tasks):
        return "[]"

    def _has_effective_changes(self, result, existing):
        return True


def test_base_task_verifier_filtering_keeps_changed_results():
    verifier = _DummyVerifier()

    class Existing:
        def __init__(self, id_):
            self.id = id_
            self.status = None
            self.priority = None
            self.assignee = None

    class Result:
        pass

    existing = [Existing("1")]
    r = Result()
    r.action = "update"
    r.task_id = "1"
    r.task_name = "t"
    r.task_status = "done"
    r.task_priority = None
    r.task_assignee = ""

    filtered = verifier._filter_unchanged_updates([r], existing)
    assert filtered == [r]
