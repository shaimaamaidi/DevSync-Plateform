"""
Domain DTO for market intelligence summary.

This module defines the MarketIntelligenceSummary DTO used to represent analyzed market insights
generated during the backlog creation workflow. It aggregates trends, competitor features, user pain
points, and best practices to guide structured backlog generation.

Main classes:
    MarketIntelligenceSummary
"""

from pydantic import BaseModel, Field
from typing import List


class MarketIntelligenceSummary(BaseModel):
    """
    Structured market intelligence used to guide backlog generation.

    This DTO summarizes extracted market knowledge, including trends, competitor analysis,
    user pain points, and recommended best practices. It is used as an input context
    for generating more relevant and user-centric backlog structures.

    Attributes:
        market_trends: Concise summary of current market trends and user expectations.
        competitor_features: Key features commonly found in competing products.
        user_pain_points: Common user problems or frustrations in the domain.
        best_practices: Recommended best practices for designing similar products.
        enrichment_notes: Final synthesis of insights to guide backlog generation.
    """
    market_trends: str = Field(
        ...,
        description="Concise summary (2-3 sentences) of current market trends and user expectations related to the project domain",
    )
    competitor_features: List[str] = Field(
        ...,
        description="List of key features commonly found in competing products or similar solutions",
    )
    user_pain_points: List[str] = Field(
        ...,
        description="List of common problems or frustrations experienced by users in this domain",
    )
    best_practices: List[str] = Field(
        ...,
        description="List of recommended best practices for designing and building this type of product",
    )
    enrichment_notes: str = Field(
        ...,
        description="Short synthesis (1-2 sentences) highlighting key insights to guide backlog generation",
    )