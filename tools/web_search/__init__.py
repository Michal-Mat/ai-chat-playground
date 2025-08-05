"""
Web Search Integration Package

This package provides web search functionality using DuckDuckGo's XML API
with data validation and types.
"""

from integrations.search import (
    DuckDuckGoClient,
    DuckDuckGoRateLimitError,
    DuckDuckGoSearchError,
)

from .exceptions import (
    SearchValidationError,
    WebSearchError,
    WebSearchToolError,
)
from .models import SearchError, SearchRequest, SearchResponse, SearchResult
from .search_tool import WebSearchTool, create_web_search_tool

__all__ = [
    # Client
    "DuckDuckGoClient",
    # Exceptions
    "WebSearchError",
    "DuckDuckGoSearchError",
    "DuckDuckGoRateLimitError",
    "WebSearchToolError",
    "SearchValidationError",
    # Models
    "SearchRequest",
    "SearchResult",
    "SearchResponse",
    "SearchError",
    # Tools
    "WebSearchTool",
    "create_web_search_tool",
]
