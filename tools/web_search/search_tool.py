"""
Web Search Tool for pydantic-ai

This module provides a web search tool that integrates with DuckDuckGo
for searching the web and retrieving current information.
"""

import logging
import time
from typing import Any

from core.config import AppConfig
from integrations.search.duckduckgo_client import DuckDuckGoClient
from integrations.search.exceptions import DuckDuckGoSearchError
from tools.web_search.models.input import WebSearchInput
from tools.web_search.models.output import WebSearchOutput

# Configure logging
logger = logging.getLogger(__name__)


class WebSearchTool:
    """
    Web search tool for pydantic-ai that searches DuckDuckGo.
    """

    def __init__(
        self,
        config: AppConfig,
        search_client: DuckDuckGoClient,
    ) -> None:
        """
        Initialize the web search tool.

        Args:
            config: Application configuration instance
            client: DuckDuckGo client instance (creates new one if None)
        """
        self.config: AppConfig = config
        self.client: DuckDuckGoClient = search_client
        self._tool_schema: dict[str, Any] = self._create_tool_schema()

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
    config: AppConfig,
    client: DuckDuckGoClient,
) -> WebSearchTool:
    """
    Create a web search tool instance.

    Args:
        config: Application configuration instance
        client: DuckDuckGo client instance (creates new one if None)

    Returns:
        WebSearchTool instance
    """
    return WebSearchTool(config=config, search_client=client)
