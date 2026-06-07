from types import SimpleNamespace

from backend.src.infrastructure.external.task_status_checking.task_status_synthesizer_agent import (
    TaskStatusSynthesizerAgent,
)


def test_task_status_synthesizer_returns_fallback_when_llm_none():
    agent = TaskStatusSynthesizerAgent(prompt_loader=object())
    agent._call_llm = lambda *a, **k: None

    class Task:
        def __init__(self):
            self.id = "t1"
            self.status = "done"

        def to_dict(self):
            return {"id": self.id}

    task = Task()
    # synthesize_task_status expects (task, commits, signals)
    result = agent.synthesize_task_status(task, commits=[], signals={})
    assert hasattr(result, "is_completed") and hasattr(result, "summary")
