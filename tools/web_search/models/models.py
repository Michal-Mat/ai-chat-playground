"""
Search Result Models

This module defines Pydantic models for web search functionality
with proper type safety and validation.
"""

import time
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator


class SearchResult(BaseModel):
    """
    Individual search result from web search.
    """

    title: str = Field(
        description="Title of the search result",
        min_length=1,
    )
    url: str = Field(
        description="URL of the search result",
        min_length=1,
    )
    snippet: str = Field(
        description="Text snippet/description of the result",
        default="",
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate that URL is properly formatted."""
        try:
            parsed = urlparse(v)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("Invalid URL format")
            return v
        except Exception as e:
            raise ValueError(f"Invalid URL: {e}") from e

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Clean and validate title."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Title cannot be empty")
        return cleaned

    @field_validator("snippet")
    @classmethod
    def validate_snippet(cls, v: str) -> str:
        """Clean snippet text."""
        return v.strip()

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            # Add any custom JSON encoders if needed
        }


class SearchRequest(BaseModel):
    """
    Search request parameters.
    """

    query: str = Field(
        description="Search query string",
        min_length=1,
        max_length=1000,
    )
    region: str = Field(
        default="us-en",
        description="Search region (e.g., us-en, uk-en)",
        pattern=r"^[a-z]{2}-[a-z]{2}$",
    )
    safesearch: str = Field(
        default="moderate",
        description="Safe search level",
        pattern=r"^(off|moderate|strict)$",
    )
    max_results: int = Field(
        description="Maximum number of results to return",
        default=10,
        ge=1,
        le=50,
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Clean and validate search query."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Query cannot be empty")
        if len(cleaned) > 1000:
            raise ValueError("Query too long (max 1000 characters)")
        return cleaned

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            # Add any custom JSON encoders if needed
        }


class SearchResponse(BaseModel):
    """
    Complete search response with results and metadata.
    """

    query: str = Field(
        description="Original search query",
    )
    results: list[SearchResult] = Field(
        description="List of search results",
        default_factory=list,
    )
    abstract: str = Field(
        description="Abstract/summary if available",
        default="",
    )
    abstract_url: str = Field(
        description="URL for abstract if available",
        default="",
    )
    total_results: int = Field(
        description="Total number of results found",
        default=0,
    )
    search_time_ms: float = Field(
        description="Search execution time in milliseconds",
        default=0.0,
    )
    source: str = Field(
        description="Search source/provider",
        default="duckduckgo",
    )

    @field_validator("abstract_url")
    @classmethod
    def validate_abstract_url(cls, v: str) -> str:
        """Validate abstract URL if provided."""
        if v and v.strip():
            try:
                parsed = urlparse(v)
                if not parsed.scheme or not parsed.netloc:
                    raise ValueError("Invalid abstract URL format")
                return v
            except Exception as e:
                raise ValueError(f"Invalid abstract URL: {e}") from e
        return v

    @property
    def has_results(self) -> bool:
        """Check if search returned any results."""
        return len(self.results) > 0

    @property
    def result_count(self) -> int:
        """Get the number of results."""
        return len(self.results)

    def get_top_result(self) -> SearchResult | None:
        """Get the first result if available."""
        return self.results[0] if self.results else None

    def get_results_by_domain(self, domain: str) -> list[SearchResult]:
        """Get results from a specific domain."""
        domain = domain.lower()
        return [
            result for result in self.results if domain in result.url.lower()
        ]

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            # Add any custom JSON encoders if needed
        }


class SearchError(BaseModel):
    """
    Search error information.
    """

    error_type: str = Field(
        description="Type of error that occurred",
    )
    error_message: str = Field(
        description="Human-readable error message",
    )
    query: str = Field(
        description="Query that caused the error",
    )
    timestamp: float = Field(
        description="Error timestamp",
        default_factory=time.time,
    )

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            # Add any custom JSON encoders if needed
        }


# Convenience type aliases
SearchResults = list[SearchResult]
SearchQuery = str


class WebSearchInput(BaseModel):
    """
    Input parameters for web search tool.
    """

    query: str = Field(
        description="Search query to execute",
        min_length=1,
        max_length=1000,
    )
    region: str = Field(
        description="Search region (e.g., us-en, uk-en)",
        pattern=r"^[a-z]{2}-[a-z]{2}$",
    )
    safesearch: str = Field(
        description="Safe search level (off, moderate, strict)",
        pattern=r"^(off|moderate|strict)$",
    )
    max_results: int = Field(
        description="Maximum number of results to return",
        ge=1,
        le=50,
    )

    def __init__(self, **data):
        # Note: This will be called during model validation, so we can't inject config here
        # The config will be used in the WebSearchTool constructor instead
        super().__init__(**data)
