#!/usr/bin/env python3
"""
Integration tests for web search functionality.

These tests make actual HTTP requests to verify the integration
with DuckDuckGo API works correctly in real scenarios.
"""

import asyncio
import logging

from core.config import get_config
from integrations.search.duckduckgo_client import DuckDuckGoClient
from tools.web_search.search_tool import WebSearchTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_sync_search_integration() -> None:
    """Test synchronous web search with real API calls."""
    logger.info("Testing synchronous web search integration...")

    try:
        config = get_config()
        with DuckDuckGoClient(config=config) as client:
            results = client.search("Python programming")

            logger.info("Search completed successfully!")
            logger.info(f"Query: {results.get('query', 'N/A')}")
            logger.info(f"Results found: {len(results.get('results', []))}")

            # Print first few results
            for i, result in enumerate(results.get("results", [])[:3]):
                logger.info(f"Result {i+1}:")
                logger.info(f"  Title: {result.get('title', 'N/A')}")
                logger.info(f"  URL: {result.get('url', 'N/A')}")
                logger.info(
                    f"  Snippet: {result.get('snippet', 'N/A')[:100]}..."
                )
                logger.info("")

    except Exception as e:
        logger.error(f"Sync search integration test failed: {e}")


async def test_async_search_integration() -> None:
    """Test asynchronous web search with real API calls."""
    logger.info("Testing asynchronous web search integration...")

    try:
        config = get_config()
        async with DuckDuckGoClient(config=config) as client:
            results = await client.async_search("AI news 2024")

            logger.info("Async search completed successfully!")
            logger.info(f"Query: {results.get('query', 'N/A')}")
            logger.info(f"Results found: {len(results.get('results', []))}")

            # Print first few results
            for i, result in enumerate(results.get("results", [])[:3]):
                logger.info(f"Result {i+1}:")
                logger.info(f"  Title: {result.get('title', 'N/A')}")
                logger.info(f"  URL: {result.get('url', 'N/A')}")
                logger.info(
                    f"  Snippet: {result.get('snippet', 'N/A')[:100]}..."
                )
                logger.info("")

    except Exception as e:
        logger.error(f"Async search integration test failed: {e}")


def test_web_search_tool_integration() -> None:
    """Test web search tool with real API calls."""
    logger.info("Testing web search tool integration...")

    try:
        config = get_config()
        client = DuckDuckGoClient(config=config)
        with WebSearchTool(config=config, search_client=client) as tool:
            result = tool("machine learning tutorials")

            logger.info("Tool search completed!")
            logger.info(f"Success: {result.success}")
            logger.info(f"Query: {result.query}")
            logger.info(f"Results: {result.total_results}")
            logger.info(f"Search time: {result.search_time_ms:.2f}ms")

            if result.success and result.results:
                logger.info("First result:")
                first_result = result.results[0]
                logger.info(f"  Title: {first_result['title']}")
                logger.info(f"  URL: {first_result['url']}")
                logger.info(f"  Snippet: {first_result['snippet'][:100]}...")
            elif not result.success:
                logger.error(f"Search failed: {result.error_message}")

    except Exception as e:
        logger.error(f"Web search tool integration test failed: {e}")


async def test_async_web_search_tool_integration() -> None:
    """Test async web search tool with real API calls."""
    logger.info("Testing async web search tool integration...")

    try:
        config = get_config()
        client = DuckDuckGoClient(config=config)
        async with WebSearchTool(config=config, search_client=client) as tool:
            result = await tool.async_call("latest AI developments")

            logger.info("Async tool search completed!")
            logger.info(f"Success: {result.success}")
            logger.info(f"Query: {result.query}")
            logger.info(f"Results: {result.total_results}")
            logger.info(f"Search time: {result.search_time_ms:.2f}ms")

            if result.success and result.results:
                logger.info("First result:")
                first_result = result.results[0]
                logger.info(f"  Title: {first_result['title']}")
                logger.info(f"  URL: {first_result['url']}")
                logger.info(f"  Snippet: {first_result['snippet'][:100]}...")
            elif not result.success:
                logger.error(f"Search failed: {result.error_message}")

    except Exception as e:
        logger.error(f"Async web search tool integration test failed: {e}")


def main() -> None:
    """Run all integration tests."""
    logger.info("Starting web search integration tests...")

    # Test sync search
    test_sync_search_integration()

    # Test web search tool
    test_web_search_tool_integration()

    # Test async search
    asyncio.run(test_async_search_integration())

    # Test async web search tool
    asyncio.run(test_async_web_search_tool_integration())

    logger.info("All integration tests completed!")


if __name__ == "__main__":
    main()
