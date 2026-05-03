"""
Service port for user backlog fixing operations.

This module defines the IUserBacklogFixer interface, which specifies operations for
comparing, validating, and correcting a user-provided backlog against a reference backlog.
"""

from abc import ABC, abstractmethod

from backend.src.domain.entities.backlog.structure import BacklogStructure
from backend.src.domain.entities.backlog.validation import BacklogValidation


class IUserBacklogFixer(ABC):
    """
    Define user backlog fixing behavior required by the application.

    This interface is responsible for validating a user-modified backlog by comparing it
    with a reference backlog structure and producing a corrected version along with validation
    results and detected issues.
    """

    @abstractmethod
    def fix_user_backlog(
        self,
        backlog_reference: BacklogStructure,
        backlog_to_validate: BacklogStructure,
    ) -> BacklogValidation:
        """
        Validate and fix a user-provided backlog.

        This method compares the user backlog against a reference backlog and returns
        a corrected version along with validation status and detected issues.

        Args:
            backlog_reference (BacklogStructure): Reference backlog used as ground truth.
            backlog_to_validate (BacklogStructure): User-provided backlog to validate and fix.

        Returns:
            BacklogValidation: Validation result containing corrected backlog and validation status.
        """
        pass