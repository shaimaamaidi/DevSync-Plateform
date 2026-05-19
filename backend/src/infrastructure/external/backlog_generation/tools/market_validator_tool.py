"""
Market intelligence validation tool.

This module provides a tool responsible for validating a market intelligence
context against a product description. It ensures consistency, correctness,
and structural compliance of the market intelligence data before further
processing in the backlog generation pipeline.

It acts as an interface between external callers (LLM tools / agents) and the
domain-level market intelligence validation service.
"""

import logging

from pydantic import ValidationError

from backend.src.domain.entities.market.intelligence import MarketIntelligenceSummary
from backend.src.domain.entities.product.initial_description import InitialDescription
from backend.src.domain.exceptions.llm.llm_api_exception import LLMApiException
from backend.src.domain.exceptions.llm.llm_network_exception import LLMNetworkException
from backend.src.domain.exceptions.llm.llm_parsing_exception import LLMParsingException
from backend.src.domain.exceptions.tool.invalid_tool_argument_exception import InvalidToolArgumentException
from backend.src.domain.exceptions.tool.tool_execution_exception import ToolExecutionException
from backend.src.domain.ports.services.backlog_generation.agents.imarket_intelligence_validator import (
    IMarketIntelligenceValidator,
)
from backend.src.domain.ports.services.backlog_generation.tools.imarket_validator_tool import (
    IMarketValidatorTool,
)


logger = logging.getLogger(__name__)


class MarketValidatorTool(IMarketValidatorTool):
    """
    Tool responsible for validating market intelligence context.

    This tool:
    - Validates and parses product description JSON
    - Validates and parses market intelligence context JSON
    - Ensures consistency between product and market data
    - Delegates validation logic to IMarketIntelligenceValidator
    - Returns validated result as JSON

    Attributes:
        market_intelligence_validator (IMarketIntelligenceValidator):
            Service responsible for validating market intelligence context.
    """

    def __init__(self, market_intelligence_validator: IMarketIntelligenceValidator) -> None:
        """
        Initialize the MarketValidatorTool.

        Args:
            market_intelligence_validator (IMarketIntelligenceValidator):
                Service used to validate market intelligence context.
        """
        self.market_intelligence_validator = market_intelligence_validator

    async def __call__(self, detailed_description: str, context: str) -> str:
        """
        Validate market intelligence context against product description.

        Args:
            detailed_description (str): JSON string representing the initial product description.
                Must match the output format of build_product_context.
            context (str): JSON string representing market intelligence data.
                Must match the output format of summarize_market_intelligence
                or validate_market_intelligence.

        Returns:
            str: JSON string representing the validated market intelligence.

        Raises:
            InvalidToolArgumentException: If detailed_description or context is not valid JSON or
                does not match the expected schema.
            ToolExecutionException: If market intelligence validation fails due to LLM errors, inconsistencies,
                service errors, or unexpected runtime issues.
        """
        logger.info(
            "MarketValidatorTool called (description_size=%s, context_size=%s).",
            len(detailed_description),
            len(context),
        )

        try:
            description_obj = InitialDescription.model_validate_json(detailed_description)
        except ValidationError as e:
            logger.warning(
                "Invalid product description format in MarketSummarizerTool.",
                extra={"input_preview": detailed_description[:200]}
            )
            raise InvalidToolArgumentException(
                "detailed_description must be the exact JSON string returned by build_product_context."
            ) from e

        try:
            context_obj = MarketIntelligenceSummary.model_validate_json(context)
        except ValidationError as e:
            logger.warning(
                "Invalid context format in MarketValidatorTool.",
                extra={"input_preview": context[:200]}
            )
            raise InvalidToolArgumentException(
                "Something went wrong while validating the market. Please try again."
            ) from e

        try:
            result = self.market_intelligence_validator.validate_context(
                description_obj,
                context_obj,
            )

            return result.model_dump_json()

        except (LLMNetworkException, LLMApiException, LLMParsingException) as e:
            logger.error("LLM error in MarketValidatorTool: %s", e)
            raise ToolExecutionException(
                "The market validation could not be generated due to an AI service error. Please try again."
            ) from e

        except Exception as e:
            logger.exception("MarketValidatorTool failed unexpectedly.")
            raise ToolExecutionException(
                "An unexpected error occurred while validating the market. Please try again or contact support."
            ) from e