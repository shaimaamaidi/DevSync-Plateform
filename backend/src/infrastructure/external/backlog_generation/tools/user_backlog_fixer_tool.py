"""
User backlog fixing tool.

This module provides a tool responsible for reconciling and correcting a user-modified
backlog against a reference backlog structure. It ensures that user edits remain
consistent with the original backlog model while preserving valid modifications.

The tool delegates the correction logic to the IUserBacklogFixer service,
which applies domain rules and structural validation.
"""

import logging

from pydantic import ValidationError

from backend.src.domain.entities.backlog.structure import BacklogStructure
from backend.src.domain.exceptions.llm.llm_api_exception import LLMApiException
from backend.src.domain.exceptions.llm.llm_network_exception import LLMNetworkException
from backend.src.domain.exceptions.llm.llm_parsing_exception import LLMParsingException
from backend.src.domain.exceptions.tool.invalid_tool_argument_exception import InvalidToolArgumentException
from backend.src.domain.exceptions.tool.tool_execution_exception import ToolExecutionException
from backend.src.domain.ports.services.backlog_generation.agents.i_user_backlog_fixer import (
    IUserBacklogFixer,
)
from backend.src.domain.ports.services.backlog_generation.tools.i_user_backlog_fixer_tool import (
    IUserBacklogFixerTool,
)


logger = logging.getLogger(__name__)


class UserBacklogFixerTool(IUserBacklogFixerTool):
    """
    Tool responsible for fixing and validating a user-modified backlog.

    This tool:
    - Validates and parses the reference backlog
    - Validates and parses the user-modified backlog
    - Delegates reconciliation logic to IUserBacklogFixer
    - Returns a corrected and validated backlog as JSON

    Attributes:
        user_backlog_fixer (IUserBacklogFixer):
            Service responsible for correcting user modifications on a backlog.
    """

    def __init__(self, user_backlog_fixer: IUserBacklogFixer) -> None:
        """
        Initialize the UserBacklogFixerTool.

        Args:
            user_backlog_fixer (IUserBacklogFixer):
                Service used to fix inconsistencies in user-edited backlog.
        """
        self.user_backlog_fixer = user_backlog_fixer

    async def __call__(
        self,
        backlog_reference: str,
        backlog_to_validate: str,
    ) -> str:
        """
        Fix a user-modified backlog using a reference backlog.

        Args:
            backlog_reference (str): JSON string representing the original validated backlog structure.
            backlog_to_validate (str): JSON string representing the user-modified backlog that needs
                validation and correction.

        Returns:
            str: JSON string representing the corrected backlog.

        Raises:
            InvalidToolArgumentException: If backlog_reference or backlog_to_validate is not valid JSON
                or does not match the expected BacklogStructure schema.
            ToolExecutionException: If backlog reconciliation fails due to LLM errors, domain rule violations,
                service errors in IUserBacklogFixer, or any unexpected runtime issue during processing.
        """
        logger.info(
            "UserBacklogFixerTool called (reference_size=%s, user_size=%s).",
            len(backlog_reference),
            len(backlog_to_validate),
        )

        try:
            backlog_reference_obj = BacklogStructure.model_validate_json(backlog_reference)
        except ValidationError as e:
            logger.warning(
                "Invalid backlog format in MarketSummarizerTool.",
                extra={"input_preview": backlog_reference[:200]}
            )
            raise InvalidToolArgumentException(
                "The reference backlog format is invalid or could not be processed. Please ensure the backlog was generated correctly and try again."
            )

        try:
            backlog_to_validate_obj = BacklogStructure.model_validate_json(backlog_to_validate)
        except ValidationError as e:
            logger.warning(
                "Invalid backlog format in MarketSummarizerTool.",
                extra={"input_preview": backlog_to_validate[:200]}
            )
            raise InvalidToolArgumentException(
                "Something went wrong while fixing your backlog. Please try again."
            ) from e

        try:
            result = self.user_backlog_fixer.fix_user_backlog(
                backlog_reference_obj,
                backlog_to_validate_obj,
            )

            logger.info("User backlog successfully fixed.")

            return result.model_dump_json()

        except (LLMNetworkException, LLMApiException, LLMParsingException) as e:
            logger.error("LLM error in UserBacklogFixerTool: %s", e)
            raise ToolExecutionException(
                "The backlog validation could not be generated due to an AI service error. Please try again."
            ) from e

        except Exception as e:
            logger.exception("UserBacklogFixerTool failed unexpectedly.")
            raise ToolExecutionException(
                "An unexpected error occurred while fixing your backlog. Please try again or contact support."
            ) from e