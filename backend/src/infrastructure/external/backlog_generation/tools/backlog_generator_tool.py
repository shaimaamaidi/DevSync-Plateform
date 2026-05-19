"""
Backlog generation tool.

This module provides a tool wrapper around the BacklogGenerationOrchestrator.
It is responsible for orchestrating the full backlog generation workflow by
validating inputs, converting them into domain objects, and delegating the
generation process to the orchestrator.

The tool acts as an interface between external callers (LLM tools / agents)
and the internal backlog generation domain logic.
"""

import logging

from pydantic import ValidationError

from backend.src.domain.entities.market.refined_intelligence import RefinedMarketIntelligenceSummary
from backend.src.domain.entities.product.initial_description import InitialDescription
from backend.src.domain.exceptions.tool.invalid_tool_argument_exception import InvalidToolArgumentException
from backend.src.domain.exceptions.tool.tool_execution_exception import ToolExecutionException
from backend.src.domain.ports.services.backlog_generation.agents.ibacklog_generation_orchestrator import (
    IBacklogGenerationOrchestrator,
)
from backend.src.domain.ports.services.backlog_generation.tools.ibacklog_generator_tool import (
    IBacklogGeneratorTool,
)


logger = logging.getLogger(__name__)


class BacklogGeneratorTool(IBacklogGeneratorTool):
    """
    Tool responsible for triggering backlog generation through the orchestrator.

    This tool:
    - Validates and parses the incoming JSON inputs
    - Converts raw strings into domain entities
    - Delegates backlog generation to the BacklogGenerationOrchestrator
    - Returns the generated backlog as a JSON string

    It is designed to be used by higher-level agents or LLM tool-calling
    pipelines as a safe and structured entry point into backlog generation.

    Attributes:
        backlog_generator (IBacklogGenerationOrchestrator):
            Orchestrator responsible for executing the backlog generation workflow.
    """

    def __init__(self, backlog_generator: IBacklogGenerationOrchestrator) -> None:
        """
        Initialize the BacklogGeneratorTool.

        Args:
            backlog_generator (IBacklogGenerationOrchestrator):
                Orchestrator responsible for executing the backlog generation workflow.
        """
        self.backlog_generator = backlog_generator

    async def __call__(self, detailed_description: str, context: str) -> str:
        """
        Execute the backlog generation process.

        Args:
            detailed_description (str): JSON string representing the initial product description.
                Must match the output format of build_product_context.
            context (str): JSON string representing refined market intelligence.
                Must match the output format of validate_market_intelligence.

        Returns:
            str: JSON string representation of the generated backlog.

        Raises:
            InvalidToolArgumentException: If detailed_description or context is not valid JSON
                or does not match the expected schema.
            ToolExecutionException: If backlog generation fails due to orchestrator errors
                or unexpected runtime issues..
        """
        logger.info(
            "BacklogGeneratorTool called.",
            extra={
                "detailed_description_size": len(detailed_description or ""),
                "context_size": len(context or "")
            }
        )

        try:
            description_obj = InitialDescription.model_validate_json(detailed_description)
        except ValidationError as e:
            logger.warning(
                "Invalid detailed_description format.",
                extra={"input_preview": detailed_description[:200]}
            )
            raise InvalidToolArgumentException(
                "Something went wrong while generating the backlog. Please try again."
            ) from e

        try:
            context_obj = RefinedMarketIntelligenceSummary.model_validate_json(context)
        except ValidationError as e:
            logger.warning(
                "Invalid context format.",
                extra={"input_preview": context[:200]}
            )
            raise InvalidToolArgumentException(
                "Something went wrong while generating the backlog. Please try again."
            ) from e

        try:
            result = await self.backlog_generator.generate(description_obj, context_obj)

            logger.info("Backlog generated successfully.")

            return result.model_dump_json()

        except Exception as e:
            logger.exception("BacklogGeneratorTool failed unexpectedly.")
            raise ToolExecutionException(
                "An unexpected error occurred while generating the backlog. Please try again or contact support."
            ) from e