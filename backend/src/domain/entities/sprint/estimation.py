"""
Domain DTO for task estimation results.

This module defines DTOs used to represent tasks enriched with effort estimation.
These models are used during sprint planning to evaluate workload, distribute tasks,
and support intelligent planning decisions.

Main classes:
    EstimatedTask, IdentifiedEstimatedTask
"""

from backend.src.domain.entities.backlog.task import Task, IdentifiedTask


class EstimatedTask(Task):
    """
    Task enriched with effort estimation.

    This DTO extends the base Task model by adding an estimation field
    representing the expected effort required to complete the task.

    Attributes:
        estimated_hours: Estimated effort required to complete the task (in hours).
    """
    estimated_hours: float

class IdentifiedEstimatedTask(IdentifiedTask):
    """
    Identified task enriched with effort estimation.

    This DTO extends IdentifiedTask by adding an estimation field
    representing the expected effort required to complete the task.

    Attributes:
        estimated_hours: Estimated effort required to complete the task (in hours).
    """
    estimated_hours: float