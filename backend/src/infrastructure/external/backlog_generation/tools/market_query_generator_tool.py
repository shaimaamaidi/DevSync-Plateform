"""
Market query generation tool.

This module provides a tool responsible for generating market research queries
from a structured product description. It acts as an interface between the
LLM-driven tool layer and the market query generation service.

The tool validates input data, converts it into a domain entity, and delegates
query generation to the IMarketQueryGenerator service.
"""

import logging

from pydantic import ValidationError

from backend.src.domain.entities.product.initial_description import InitialDescription
from backend.src.domain.exceptions.tool.invalid_tool_argument_exception import InvalidToolArgumentException
from backend.src.domain.exceptions.tool.tool_execution_exception import ToolExecutionException
from backend.src.domain.ports.services.backlog_generation.agents.imarket_query_generator import (
    IMarketQueryGenerator,
)
from backend.src.domain.ports.services.backlog_generation.tools.imarket_query_generator_tool import (
    IMarketQueryGeneratorTool,
)


logger = logging.getLogger(__name__)


class MarketQueryGeneratorTool(IMarketQueryGeneratorTool):
    """
    Tool responsible for generating market queries from a product description.

    This tool:
    - Validates and parses the incoming product description JSON
    - Converts raw input into an InitialDescription domain entity
    - Delegates query generation to IMarketQueryGenerator
    - Returns generated market queries as JSON

    Attributes:
        market_query_generator (IMarketQueryGenerator):
            Service responsible for generating market queries from product data.
    """

    def __init__(self, market_query_generator: IMarketQueryGenerator) -> None:
        """
        Initialize the MarketQueryGeneratorTool.

        Args:
            market_query_generator (IMarketQueryGenerator): Service used to generate market queries.
        """
        self.market_query_generator = market_query_generator

    async def __call__(self, detailed_description: str) -> str:
        """
        Generate market queries from a product description.

        Args:
            detailed_description (str): JSON string representing the initial product description.
                Must match the output format of build_product_context.

        Returns:
            str: JSON string containing generated market queries.

        Raises:
            InvalidToolArgumentException: If detailed_description is not valid JSON or does not match
                the expected schema.
            ToolExecutionException: If market query generation fails due to service errors or
                unexpected runtime issues.
        """
        logger.info(
            "MarketQueryGeneratorTool called.",
            extra={
                "input_size": len(detailed_description or "")
            }
        )

        try:
            description_obj = InitialDescription.model_validate_json(detailed_description)
        except ValidationError as e:
            logger.warning(
                "Invalid product description format in MarketQueryGeneratorTool.",
                extra={"input_preview": detailed_description[:200]}
            )
            raise InvalidToolArgumentException(
                "detailed_description must be the exact JSON string returned by build_product_context."
            ) from e

        try:
            result = self.market_query_generator.generate_queries(description_obj)

            logger.info("Market queries generated successfully.")

            return result.model_dump_json()
        except Exception as e:
            logger.exception("MarketQueryGeneratorTool failed unexpectedly.")
            raise ToolExecutionException(
                f"Market query generation failed: {str(e)}."
            ) from e