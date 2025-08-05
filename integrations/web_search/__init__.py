"""
Web Search Integration Package

This package provides web search functionality using DuckDuckGo's XML API
with data validation and types.
"""

from ..search.duckduckgo_client import DuckDuckGoClient
from .config import DuckDuckGoClientConfig, WebSearchToolConfig
from .exceptions import (
    DuckDuckGoRateLimitError,
    DuckDuckGoSearchError,
    SearchValidationError,
    WebSearchError,
    WebSearchToolError,
)
from .models import SearchError, SearchRequest, SearchResponse, SearchResult
from .search_tool import WebSearchTool, create_web_search_tool

__all__ = [
    # Config
    "DuckDuckGoClientConfig",
    "WebSearchToolConfig",
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
