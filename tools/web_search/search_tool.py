"""
Web Search Tool for Pydantic-AI

This module defines a web search tool using pydantic-ai that can be used
with AI agents to perform web searches via DuckDuckGo.
"""

import logging
import time
from typing import Any

from pydantic import BaseModel, Field

from core.config import get_config
from integrations.search import DuckDuckGoClient
from integrations.search.exceptions import DuckDuckGoSearchError

# Configure logging
logger = logging.getLogger(__name__)


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
        config = get_config()
        # Set defaults from centralized config if not provided
        if "region" not in data:
            data["region"] = config.web_search_default_region
        if "safesearch" not in data:
            data["safesearch"] = config.web_search_default_safesearch
        if "max_results" not in data:
            data["max_results"] = config.web_search_max_results
        super().__init__(**data)


class WebSearchOutput(BaseModel):
    """
    Output from web search tool.
    """

    success: bool = Field(
        description="Whether the search was successful",
    )
    query: str = Field(
        description="Original search query",
    )
    results: list[dict[str, str]] = Field(
        description="List of search results with title, url, and snippet",
        default_factory=list,
    )
    total_results: int = Field(
        description="Total number of results found",
        default=0,
    )
    search_time_ms: float = Field(
        description="Search execution time in milliseconds",
        default=0.0,
    )
    error_message: str = Field(
        description="Error message if search failed",
        default="",
    )
    source: str = Field(
        description="Search source/provider",
        default="duckduckgo",
    )


class WebSearchTool:
    """
    Web search tool for pydantic-ai that searches DuckDuckGo.
    """

    def __init__(
        self,
        client: DuckDuckGoClient | None = None,
    ) -> None:
        """
        Initialize the web search tool.

        Args:
            client: DuckDuckGo client instance (creates new one if None)
        """
        self.client = client or DuckDuckGoClient()
        self.config = get_config()
        self._tool_schema = self._create_tool_schema()

        logger.info("Web search tool initialized")

    def _create_tool_schema(self) -> dict[str, Any]:
        """Create the tool schema for pydantic-ai."""
        return {
            "name": "web_search",
            "description": (
                "Search the web for information using DuckDuckGo. "
                "Useful for finding current information, news, facts, "
                "or any information that might be available online."
            ),
            "input_model": WebSearchInput,
            "output_model": WebSearchOutput,
        }

    @property
    def schema(self) -> dict[str, Any]:
        """Get the tool schema."""
        return self._tool_schema

    def __call__(
        self,
        query: str,
        region: str | None = None,
        safesearch: str | None = None,
        max_results: int | None = None,
    ) -> WebSearchOutput:
        """
        Execute web search synchronously.

        Args:
            query: Search query
            region: Search region
            safesearch: Safe search level
            max_results: Maximum number of results

        Returns:
            Search results
        """
        start_time = time.time()

        try:
            # Use centralized config defaults if parameters are None
            if region is None:
                region = self.config.web_search_default_region
            if safesearch is None:
                safesearch = self.config.web_search_default_safesearch
            if max_results is None:
                max_results = self.config.web_search_max_results

            # Validate input
            search_input = WebSearchInput(
                query=query,
                region=region,
                safesearch=safesearch,
                max_results=max_results,
            )

            # Perform search
            raw_results = self.client.search(
                query=search_input.query,
                region=search_input.region,
                safesearch=search_input.safesearch,
            )

            # Process results
            results = []
            for result in raw_results.get("results", [])[:max_results]:
                results.append(
                    {
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "snippet": result.get("snippet", ""),
                    }
                )

            search_time = (time.time() - start_time) * 1000

            logger.info(
                f"Web search completed: {len(results)} results for '{query}'"
            )

            return WebSearchOutput(
                success=True,
                query=search_input.query,
                results=results,
                total_results=len(results),
                search_time_ms=search_time,
                source="duckduckgo",
            )

        except DuckDuckGoSearchError as e:
            search_time = (time.time() - start_time) * 1000
            logger.error(f"Web search failed for '{query}': {e}")

            return WebSearchOutput(
                success=False,
                query=query,
                error_message=str(e),
                search_time_ms=search_time,
                source="duckduckgo",
            )

        except Exception as e:
            search_time = (time.time() - start_time) * 1000
            logger.error(f"Unexpected error in web search for '{query}': {e}")

            return WebSearchOutput(
                success=False,
                query=query,
                error_message=f"Unexpected error: {e}",
                search_time_ms=search_time,
                source="duckduckgo",
            )

    async def async_call(
        self,
        query: str,
        region: str | None = None,
        safesearch: str | None = None,
        max_results: int | None = None,
    ) -> WebSearchOutput:
        """
        Execute web search asynchronously.

        Args:
            query: Search query
            region: Search region
            safesearch: Safe search level
            max_results: Maximum number of results

        Returns:
            Search results
        """
        start_time = time.time()

        try:
            # Use centralized config defaults if parameters are None
            if region is None:
                region = self.config.web_search_default_region
            if safesearch is None:
                safesearch = self.config.web_search_default_safesearch
            if max_results is None:
                max_results = self.config.web_search_max_results

            # Validate input
            search_input = WebSearchInput(
                query=query,
                region=region,
                safesearch=safesearch,
                max_results=max_results,
            )

            # Perform async search
            raw_results = await self.client.async_search(
                query=search_input.query,
                region=search_input.region,
                safesearch=search_input.safesearch,
            )

            # Process results
            results = []
            for result in raw_results.get("results", [])[:max_results]:
                results.append(
                    {
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "snippet": result.get("snippet", ""),
                    }
                )

            search_time = (time.time() - start_time) * 1000

            logger.info(
                f"Async web search completed: {len(results)} results for '{query}'"
            )

            return WebSearchOutput(
                success=True,
                query=search_input.query,
                results=results,
                total_results=len(results),
                search_time_ms=search_time,
                source="duckduckgo",
            )

        except DuckDuckGoSearchError as e:
            search_time = (time.time() - start_time) * 1000
            logger.error(f"Async web search failed for '{query}': {e}")

            return WebSearchOutput(
                success=False,
                query=query,
                error_message=str(e),
                search_time_ms=search_time,
                source="duckduckgo",
            )

        except Exception as e:
            search_time = (time.time() - start_time) * 1000
            logger.error(
                f"Unexpected error in async web search for '{query}': {e}"
            )

            return WebSearchOutput(
                success=False,
                query=query,
                error_message=f"Unexpected error: {e}",
                search_time_ms=search_time,
                source="duckduckgo",
            )

    def close(self) -> None:
        """Close the tool and clean up resources."""
        if self.client:
            self.client.close()

        logger.info("Web search tool closed")

    async def aclose(self) -> None:
        """Close the tool and clean up resources (async)."""
        if self.client:
            await self.client.aclose()

        logger.info("Web search tool closed (async)")

    def __enter__(self) -> "WebSearchTool":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

    async def __aenter__(self) -> "WebSearchTool":
        """Async context manager entry."""
        return self

    async def __aexit__(
        self, exc_type: Any, exc_val: Any, exc_tb: Any
    ) -> None:
        """Async context manager exit."""
        await self.aclose()


# Convenience function to create a web search tool
def create_web_search_tool(
    client: DuckDuckGoClient | None = None,
) -> WebSearchTool:
    """
    Create a web search tool instance.

    Args:
        client: DuckDuckGo client instance (creates new one if None)

    Returns:
        WebSearchTool instance
    """
    return WebSearchTool(client=client)
