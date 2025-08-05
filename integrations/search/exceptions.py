"""
Search Integration Exceptions

This module defines custom exceptions for search functionality.
"""


class SearchError(Exception):
    """Base exception for search errors."""

    pass


class DuckDuckGoSearchError(SearchError):
    """Custom exception for DuckDuckGo search errors."""

    pass


class DuckDuckGoRateLimitError(DuckDuckGoSearchError):
    """Exception raised when rate limit is exceeded."""

    pass
