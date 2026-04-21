"""
Product context building tool.

This module provides a tool responsible for transforming a raw product
description into a structured product context. It acts as the first step in
the market and backlog generation pipeline by normalizing and enriching
the initial user input.

The tool delegates the actual context construction to the
IProductContextBuilder service.
"""

import logging

from backend.src.domain.exceptions.tool_execution_exception import ToolExecutionException
from backend.src.domain.ports.services.backlog_generation.agents.iproduct_context_builder import (
    IProductContextBuilder,
)
from backend.src.domain.ports.services.backlog_generation.tools.iproduct_context_builder_tool import (
    IProductContextTool,
)


logger = logging.getLogger(__name__)


class ProductContextBuilderTool(IProductContextTool):
    """
    Tool responsible for building a structured product context.

    This tool:
    - Receives a raw product description
    - Delegates context construction to IProductContextBuilder
    - Returns a structured product context as JSON

    Attributes:
        product_context_builder (IProductContextBuilder):
            Service responsible for building enriched product context.
    """

    def __init__(self, product_context_builder: IProductContextBuilder) -> None:
        """
        Initialize the ProductContextBuilderTool.

        Args:
            product_context_builder (IProductContextBuilder):
                Service used to build product context from raw description.
        """
        self.product_context_builder = product_context_builder

    async def __call__(self, description: str) -> str:
        """
        Build a structured product context from a raw description.

        Args:
            description (str): Raw product description provided by the user or upstream system.

        Returns:
            str: JSON string representing the structured product context.

        Raises:
            ToolExecutionException: If product context building fails due to service errors
                in IProductContextBuilder or any unexpected runtime issue during processing
                of the raw product description.
        """
        logger.info(
            "ProductContextBuilderTool called (description_length=%s).",
            len(description),
        )

        try:
            result = self.product_context_builder.build_context(description)

            logger.info("Product context successfully built.")

            return result.model_dump_json()
        except Exception as e:
            logger.exception("ProductContextBuilderTool failed unexpectedly.")
            raise ToolExecutionException(
                f"Product context build failed: {str(e)}."
            ) from e