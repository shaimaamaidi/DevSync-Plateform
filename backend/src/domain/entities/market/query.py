"""
Domain DTO for query generation output.

This module defines the QueryGeneration DTO used to represent a set of generated search queries.
It is typically used in workflows where the system needs to generate structured queries for
market research, information retrieval, or intelligence gathering.

Main classes:
    QueryGeneration
"""

from pydantic import BaseModel, Field
from typing import List


class QueryGeneration(BaseModel):
    """
    Container for generated search queries.

    This DTO encapsulates a list of search queries produced by the system,
    usually as part of a market intelligence or research pipeline.

    Attributes:
        queries: List of generated search query strings.
    """
    queries: List[str] = Field(..., description="List of generated search queries")