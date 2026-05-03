"""
Domain DTO for backlog validation results.

This module defines the BacklogValidation DTO used to represent the result of a backlog validation process.
It includes the corrected backlog structure, a list of detected corrections, and a validation flag indicating
whether the backlog is valid or requires improvements.

Main classes:
    BacklogValidation
"""

from pydantic import BaseModel
from typing import List

from backend.src.domain.entities.backlog.structure import BacklogStructure


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
    corrections: List[str]
    is_valid: bool