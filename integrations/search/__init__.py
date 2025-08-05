"""
Search Integration Package

This package provides search functionality using DuckDuckGo's XML API
with proper error handling and rate limiting.
"""

from .duckduckgo_client import DuckDuckGoClient
from .exceptions import (
    DuckDuckGoRateLimitError,
    DuckDuckGoSearchError,
    SearchError,
)

__all__ = [
    # Client
    "DuckDuckGoClient",
    # Exceptions
    "SearchError",
    "DuckDuckGoSearchError",
    "DuckDuckGoRateLimitError",
]
