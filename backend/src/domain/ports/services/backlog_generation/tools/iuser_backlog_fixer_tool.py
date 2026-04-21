"""
Service port for user backlog fixing tool.

This module defines the IUserBacklogFixerTool interface, which specifies a callable contract
for validating and correcting a user-provided backlog by comparing it with a reference backlog.
It ensures consistency, structure integrity, and alignment with expected standards.
"""

from abc import ABC, abstractmethod


class IUserBacklogFixerTool(ABC):
    """
    Define user backlog fixing tool behavior required by the application.

    This interface represents a callable tool responsible for comparing a reference backlog
    with a user-provided backlog, detecting inconsistencies, and producing a corrected and
    validated version of the backlog.
    """

    @abstractmethod
    async def __call__(
        self,
        backlog_reference: str,
        backlog_to_validate: str,
    ) -> str:
        """
        Validate and fix a user-provided backlog against a reference.

        Args:
            backlog_reference (str): Reference backlog used as the expected structure.
            backlog_to_validate (str): User-provided backlog to validate and correct.

        Returns:
            str: Corrected and validated backlog as structured or serialized text.
        """
        pass