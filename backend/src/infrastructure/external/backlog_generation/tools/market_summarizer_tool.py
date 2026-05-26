"""
Market intelligence summarization tool.

This module provides a tool responsible for generating a refined market
intelligence summary based on a product description and optional web results.

It acts as an interface between external LLM/tooling systems and the internal
market intelligence summarization service, ensuring proper validation and
routing of inputs to the domain logic.
"""

import logging

from typing import Optional

from pydantic import ValidationError

from backend.src.domain.entities.product.initial_description import InitialDescription
from backend.src.domain.exceptions.llm.llm_api_exception import LLMApiException
from backend.src.domain.exceptions.llm.llm_network_exception import LLMNetworkException
from backend.src.domain.exceptions.llm.llm_parsing_exception import LLMParsingException
from backend.src.domain.exceptions.tool.invalid_tool_argument_exception import InvalidToolArgumentException
from backend.src.domain.exceptions.tool.tool_execution_exception import ToolExecutionException
from backend.src.domain.ports.services.backlog_generation.agents.i_market_intelligence_summarizer import (
    IMarketIntelligenceSummarizer,
)
from backend.src.domain.ports.services.backlog_generation.tools.i_market_summarizer_tool import (
    IMarketSummarizerTool,
)


logger = logging.getLogger(__name__)


class MarketSummarizerTool(IMarketSummarizerTool):
    """
    Tool responsible for summarizing market intelligence.

    This tool:
    - Validates and parses the incoming product description JSON
    - Optionally incorporates web search results if provided
    - Delegates summarization to IMarketIntelligenceSummarizer
    - Returns a structured market intelligence summary as JSON

    Attributes:
        market_intelligence_summarizer (IMarketIntelligenceSummarizer):
            Service responsible for generating refined market intelligence
            from product data and optional web results.
    """

    def __init__(self, market_intelligence_summarizer: IMarketIntelligenceSummarizer) -> None:
        """
        Initialize the MarketSummarizerTool.

        Args:
            market_intelligence_summarizer (IMarketIntelligenceSummarizer):
                Service used to summarize market intelligence.
        """
        self.market_intelligence_summarizer = market_intelligence_summarizer

    async def __call__(self, detailed_description: str, web_result: Optional[str] = None) -> str:
        """
        Generate a market intelligence summary.

        Args:
            detailed_description (str): JSON string representing the initial product description.
                Must match the output format of build_product_context.
            web_result (Optional[str]): Optional raw web search result used to enrich the summarization.

        Returns:
            str: JSON string representing the refined market intelligence summary.

        Raises:
            InvalidToolArgumentException: If detailed_description is not valid JSON or does not
                match the expected schema.
            ToolExecutionException: If market intelligence summarization fails due to LLM errors, service
                errors, optional web result processing issues, or unexpected runtime errors.
        """
        logger.info(
            "MarketSummarizerTool called.",
            extra={
                "description_size": len(detailed_description or ""),
                "has_web_result": bool(web_result)
            }
        )

        try:
            description_obj = InitialDescription.model_validate_json(detailed_description)
        except ValidationError as e:
            logger.warning(
                "Invalid product description format in MarketSummarizerTool.",
                extra={"input_preview": detailed_description[:200]}
            )
            raise InvalidToolArgumentException(
                "Something went wrong while summarizing the market. Please try again."
            ) from e

        try:
            if web_result and web_result != "":
                logger.info(
                    "Summarizing market intelligence with web results.",
                    extra={"web_result_size": len(web_result or "")}
                )

                result = self.market_intelligence_summarizer.summarize_context(
                    description_obj,
                    web_result,
                )
            else:
                logger.info("Summarizing market intelligence without web results.")

                result = self.market_intelligence_summarizer.summarize_context(description_obj)

            logger.info("Market intelligence summary generated successfully.")

            return result.model_dump_json()

        except (LLMNetworkException, LLMApiException, LLMParsingException) as e:
            logger.error("LLM error in MarketSummarizerTool: %s", e)
            raise ToolExecutionException(
                "The market summary could not be generated due to an AI service error. Please try again."
            ) from e

        except Exception as e:
            logger.exception("MarketSummarizerTool failed unexpectedly.")
            raise ToolExecutionException(
                "An unexpected error occurred while summarizing the market. Please try again or contact support."
            ) from e