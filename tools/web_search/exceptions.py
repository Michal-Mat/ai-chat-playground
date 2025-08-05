"""
Web Search Exceptions

This module defines custom exceptions for web search functionality.
"""


class WebSearchError(Exception):
    """Base exception for web search errors."""

    pass


class WebSearchToolError(WebSearchError):
    """Exception for web search tool errors."""

    pass


class SearchValidationError(WebSearchError):
    """Exception for search validation errors."""

    pass
