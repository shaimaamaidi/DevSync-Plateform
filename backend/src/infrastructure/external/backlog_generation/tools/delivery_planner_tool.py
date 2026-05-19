"""
Delivery planning tool.

This module provides a tool responsible for transforming a validated backlog
into a structured delivery plan. It orchestrates prioritization and sprint
planning by delegating work to dedicated domain services.

The tool acts as an entry point between raw backlog input and the delivery
planning pipeline, ensuring that the backlog is properly validated, prioritized,
and organized into sprints.
"""

import logging

from pydantic import ValidationError

from backend.src.domain.entities.backlog.structure import BacklogStructure
from backend.src.domain.exceptions.llm.llm_api_exception import LLMApiException
from backend.src.domain.exceptions.llm.llm_network_exception import LLMNetworkException
from backend.src.domain.exceptions.llm.llm_parsing_exception import LLMParsingException
from backend.src.domain.exceptions.tool.invalid_tool_argument_exception import InvalidToolArgumentException
from backend.src.domain.exceptions.tool.tool_execution_exception import ToolExecutionException
from backend.src.domain.ports.services.backlog_generation.agents.ibacklog_prioritizer import (
    IBacklogPrioritizer,
)
from backend.src.domain.ports.services.backlog_generation.agents.isprint_planner import (
    ISprintPlanner,
)
from backend.src.domain.ports.services.backlog_generation.tools.idelivery_planner_tool import (
    IDeliveryPlannerTool,
)


logger = logging.getLogger(__name__)


class DeliveryPlannerTool(IDeliveryPlannerTool):
    """
    Tool responsible for generating a delivery plan from a backlog.

    This tool performs the following steps:
    - Validates and parses the incoming backlog JSON
    - Delegates prioritization of backlog items to IBacklogPrioritizer
    - Generates sprint structure using ISprintPlanner
    - Returns a structured delivery plan as JSON

    Attributes:
        backlog_prioritizer (IBacklogPrioritizer): Service responsible for prioritizing backlog items.
        sprint_planner (ISprintPlanner): Service responsible for organizing prioritized items
            into sprints.
    """

    def __init__(
        self,
        backlog_prioritizer: IBacklogPrioritizer,
        sprint_planner: ISprintPlanner,
    ) -> None:
        """
        Initialize the DeliveryPlannerTool.

        Args:
            backlog_prioritizer (IBacklogPrioritizer): Service used to prioritize backlog items.
            sprint_planner (ISprintPlanner): Service used to generate sprint planning from
                prioritized backlog.
        """
        self.backlog_prioritizer = backlog_prioritizer
        self.sprint_planner = sprint_planner

    async def __call__(self, backlog: str) -> str:
        """
        Generate a delivery plan from a backlog.

        Args:
            backlog (str): JSON string representing a validated backlog structure.
                Must match the output format of backlog_fixer_tool.

        Returns:
            str: JSON string representing the prioritized backlog and sprint plan.

        Raises:
            InvalidToolArgumentException: If backlog is not valid JSON or does not match the
                expected schema.
            ToolExecutionException: If delivery planning fails due to LLM errors, prioritization issues,
                sprint planning failure, or unexpected runtime errors.

        Notes:
            The process includes:
            1. Parsing and validating the backlog
            2. Prioritizing backlog items
            3. Generating sprint structure
        """
        logger.info(
            "DeliveryPlannerTool called.",
            extra={
                "backlog_size": len(backlog or "")
            }
        )

        try:
            backlog_obj = BacklogStructure.model_validate_json(backlog)
        except ValidationError as e:
            logger.warning(
                "Invalid backlog format.",
                extra={"input_preview": backlog[:200]}
            )
            raise InvalidToolArgumentException(
                "Something went wrong while generating your delivery plan. Please try again."
            ) from e

        try:
            result = self.backlog_prioritizer.prioritize(backlog_obj)

            logger.info("Backlog prioritization completed.")

            result = self.sprint_planner.generate_sprints(result)

            logger.info("Sprint planning generated successfully.")

            logger.info("Delivery plan generated successfully.")

            return result.model_dump_json()

        except (LLMNetworkException, LLMApiException, LLMParsingException) as e:
            logger.error("LLM error in DeliveryPlannerTool: %s", e)
            raise ToolExecutionException(
                "The delivery plan could not be generated due to an AI service error. Please try again."
            ) from e

        except Exception as e:
            logger.exception("DeliveryPlannerTool failed unexpectedly.")
            raise ToolExecutionException(
                "An unexpected error occurred while generating the delivery plan. Please try again or contact support."
            ) from e