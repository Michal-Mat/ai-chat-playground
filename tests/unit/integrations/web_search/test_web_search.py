#!/usr/bin/env python3
"""
Simple test script for web search functionality.
"""

import asyncio
import logging

from integrations.search import DuckDuckGoClient
from tools.web_search import WebSearchTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_sync_search() -> None:
    """Test synchronous web search."""
    logger.info("Testing synchronous web search...")

    try:
        with DuckDuckGoClient() as client:
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
        logger.error(f"Sync search test failed: {e}")


async def test_async_search() -> None:
    """Test asynchronous web search."""
    logger.info("Testing asynchronous web search...")

    try:
        async with DuckDuckGoClient() as client:
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
        logger.error(f"Async search test failed: {e}")


def test_web_search_tool() -> None:
    """Test web search tool."""
    logger.info("Testing web search tool...")

    try:
        with WebSearchTool() as tool:
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
        logger.error(f"Web search tool test failed: {e}")


async def test_async_web_search_tool() -> None:
    """Test async web search tool."""
    logger.info("Testing async web search tool...")

    try:
        async with WebSearchTool() as tool:
            result = await tool.async_call("Python async programming")

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
        logger.error(f"Async web search tool test failed: {e}")


def main() -> None:
    """Run all tests."""
    logger.info("Starting web search tests...")

    # Test sync search
    test_sync_search()

    # Test web search tool
    test_web_search_tool()

    # Test async search
    asyncio.run(test_async_search())

    # Test async web search tool
    asyncio.run(test_async_web_search_tool())

    logger.info("All tests completed!")


if __name__ == "__main__":
    main()
