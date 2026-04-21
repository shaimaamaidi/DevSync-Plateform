"""
Domain DTO for initial product description.

This module defines the InitialDescription DTO used to represent a structured version of the
initial user input describing a product. It is typically used as the starting point of the
backlog generation workflow to extract key functional and business information.

Main classes:
    InitialDescription
"""

from pydantic import BaseModel, Field
from typing import List


class InitialDescription(BaseModel):
    """
    Structured representation of the initial product description.

    This DTO captures the essential information provided at the beginning of the workflow,
    including product vision, target users, features, business goals, and constraints.
    It is used as input for market analysis and backlog generation.

    Attributes:
        product_overview: High-level overview of the product and its purpose.
        target_users: Main target users or personas of the product.
        core_features: Main features the product should provide.
        business_goals: Business objectives or expected outcomes.
        constraints: Constraints such as security, regulations, or performance requirements.
        summary: Short synthesis of the entire product description.
    """
    product_overview: str = Field(
        ...,
        description="High-level overview of the product and its purpose",
    )
    target_users: List[str] = Field(
        ...,
        description="Main target users or personas of the product",
    )
    core_features: List[str] = Field(
        ...,
        description="Main features the product should provide",
    )
    business_goals: List[str] = Field(
        ...,
        description="Business objectives or expected outcomes",
    )
    constraints: List[str] = Field(
        ...,
        description="Constraints such as security, regulations, or performance requirements",
    )
    summary: str = Field(
        ...,
        description="Short synthesis of the whole project (2-3 sentences)",
    )