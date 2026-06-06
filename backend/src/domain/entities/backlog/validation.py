"""
Domain DTO for backlog validation results.

This module defines the BacklogValidation DTO used to represent the result of a backlog validation process.
It includes the corrected backlog structure, a list of detected corrections, and a validation flag indicating
whether the backlog is valid or requires improvements.

Main classes:
    EpicValidation, BacklogValidation
"""

from pydantic import BaseModel, Field
from typing import List

from backend.src.domain.entities.backlog.structure import BacklogStructure, EpicBacklog


class EpicValidation(BaseModel):
    """
    Validation result for a single epic reconciliation.

    Attributes:
        corrected_epic: The fully corrected epic with all user stories and tasks.
        corrections: List of human-readable sentences describing substantive changes.
        is_valid: True only if no substantive correction was applied to this epic.
    """
    corrected_epic: EpicBacklog
    corrections: List[str] = Field(default_factory=list)
    is_valid: bool

class BacklogValidation(BaseModel):
    """
    Result of backlog validation process.

    This DTO is used to encapsulate the outcome of validating a generated or user-modified backlog.
    It provides the corrected version of the backlog, a list of identified issues or corrections,
    and a flag indicating whether the backlog is valid.

    Attributes:
        corrected_backlog: Backlog structure after applying corrections.
        corrections: List of validation issues or improvement suggestions.
        is_valid: Indicates whether the backlog is valid (True) or requires fixes (False).
    """
    corrected_backlog: BacklogStructure
    corrections: List[str] =  []
    is_valid: bool