"""
Domain DTO for refined market intelligence summary.

This module defines the RefinedMarketIntelligenceSummary DTO used to represent the validated or corrected
version of a market intelligence analysis. It is typically produced after a validation or refinement step
to ensure consistency and correctness of generated insights before backlog generation.

Main classes:
    RefinedMarketIntelligenceSummary
"""

from pydantic import BaseModel, Field
from typing import List


class RefinedMarketIntelligenceSummary(BaseModel):
    """
    Refined market intelligence used for validated backlog generation.

    This DTO represents either the original or corrected version of market intelligence data.
    It includes refined insights, validation status, and optional reasoning explaining modifications.

    Attributes:
        refined_market_trends: Refined or unchanged summary of market trends and expectations.
        refined_competitor_features: Refined or unchanged list of competitor features.
        refined_user_pain_points: Refined or unchanged list of user pain points.
        refined_best_practices: Refined or unchanged list of best practices.
        refined_enrichment_notes: Refined or unchanged synthesis of key insights.
        cause: Explanation of changes made if inconsistencies were found.
        is_valid: Indicates whether the input context is valid or has been corrected.
    """
    refined_market_trends: str = Field(
        ...,
        description="The refined or unchanged summary (2-3 sentences) of current market trends and user expectations related to the project domain",
    )
    refined_competitor_features: List[str] = Field(
        ...,
        description="The refined or unchanged list of key features commonly found in competing products or similar solutions",
    )
    refined_user_pain_points: List[str] = Field(
        ...,
        description="The refined or unchanged list of common problems or frustrations experienced by users in this domain",
    )
    refined_best_practices: List[str] = Field(
        ...,
        description="The refined or unchanged list of recommended best practices for designing and building this type of product",
    )
    refined_enrichment_notes: str = Field(
        ...,
        description="The refined or unchanged synthesis (1-2 sentences) highlighting key insights to guide backlog generation",
    )
    cause: str = Field(
        default="",
        description="Reason for any changes made if inconsistencies were found",
    )
    is_valid: bool = Field(
        ...,
        description="Whether or not the input context was validated",
    )