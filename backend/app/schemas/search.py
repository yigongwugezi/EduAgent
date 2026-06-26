"""Pydantic schemas for the web search API endpoint.

These models are used by the ``POST /api/search`` diagnostic endpoint.
The internal search service uses lightweight :mod:`dataclasses` instead.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Search request payload."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Search query string",
    )
    max_results: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of results to return",
    )


class SearchResultItem(BaseModel):
    """A single search result."""

    title: str = ""
    url: str = ""
    snippet: str = ""
    content: str = ""
    source: str = ""


class SearchResponseData(BaseModel):
    """Aggregated search response data."""

    query: str
    results: list[SearchResultItem]
    total_estimated: int = 0
    source: str = ""
    cached: bool = False
