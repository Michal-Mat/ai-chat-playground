"""
DuckDuckGo XML API Client

This module provides a client for the DuckDuckGo XML API with proper
error handling, rate limiting, and async support.
"""

import asyncio
import logging
import time
from typing import Any
from xml.etree import ElementTree

import aiohttp
import requests

from core.config import AppConfig
from integrations.search.exceptions import DuckDuckGoSearchError

logger = logging.getLogger(__name__)


class DuckDuckGoClient:
    """
    Client for DuckDuckGo XML API with proper error handling and rate limiting.
    """

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize the DuckDuckGo client using injected configuration.

        Args:
            config: Application configuration instance
        """
        self.config: AppConfig = config
        self.session: requests.Session | None = None
        self.async_session: aiohttp.ClientSession | None = None
        self._last_request_time: float = 0.0

        logger.info("DuckDuckGo client initialized")

    def _ensure_session(self) -> requests.Session:
        """Ensure a requests session is available."""
        if self.session is None:
            self.session = requests.Session()
            self.session.headers.update(
                {
                    "User-Agent": self.config.web_search_user_agent,
                }
            )
        return self.session

    async def _ensure_async_session(self) -> aiohttp.ClientSession:
        """Ensure an aiohttp session is available."""
        if self.async_session is None:
            self.async_session = aiohttp.ClientSession(
                headers={"User-Agent": self.config.web_search_user_agent},
                timeout=aiohttp.ClientTimeout(
                    total=self.config.web_search_timeout
                ),
            )
        return self.async_session

    def _rate_limit_check(self) -> None:
        """Check and enforce rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time

        if time_since_last < self.config.web_search_rate_limit_delay:
            sleep_time = (
                self.config.web_search_rate_limit_delay - time_since_last
            )
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)

        self._last_request_time = time.time()

    def _parse_xml_response(self, xml_content: str) -> dict[str, Any]:
        """
        Parse XML response from DuckDuckGo API.

        Args:
            xml_content: Raw XML content from API

        Returns:
            Parsed response as dictionary

        Raises:
            DuckDuckGoSearchError: If XML parsing fails
        """
        try:
            root = ElementTree.fromstring(xml_content)

            # Extract search results
            results = []
            for result in root.findall(".//Result"):
                result_data = {}

                # Extract title
                title_elem = result.find("Title")
                if title_elem is not None:
                    result_data["title"] = title_elem.text or ""

                # Extract URL
                url_elem = result.find("FirstURL")
                if url_elem is not None:
                    result_data["url"] = url_elem.text or ""

                # Extract snippet
                snippet_elem = result.find("Text")
                if snippet_elem is not None:
                    result_data["snippet"] = snippet_elem.text or ""

                if result_data:  # Only add if we have some data
                    results.append(result_data)

            # Extract abstract if available
            abstract = ""
            abstract_elem = root.find(".//Abstract")
            if abstract_elem is not None and abstract_elem.text:
                abstract = abstract_elem.text

            # Extract abstract URL if available
            abstract_url = ""
            abstract_url_elem = root.find(".//AbstractURL")
            if abstract_url_elem is not None and abstract_url_elem.text:
                abstract_url = abstract_url_elem.text

            return {
                "results": results,
                "abstract": abstract,
                "abstract_url": abstract_url,
                "query": root.get("query", ""),
            }

        except ElementTree.ParseError as e:
            logger.error(f"Failed to parse XML response: {e}")
            raise DuckDuckGoSearchError(f"Invalid XML response: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error parsing XML: {e}")
            raise DuckDuckGoSearchError(f"Error parsing response: {e}") from e

    def search(
        self,
        query: str,
        region: str = "us-en",
        safesearch: str = "moderate",
    ) -> dict[str, Any]:
        """
        Perform a synchronous web search using DuckDuckGo XML API.

        Args:
            query: Search query string
            region: Search region (default: us-en)
            safesearch: Safe search level (default: moderate)

        Returns:
            Parsed search results

        Raises:
            DuckDuckGoSearchError: If search fails
            DuckDuckGoRateLimitError: If rate limit is exceeded
        """
        if not query.strip():
            raise DuckDuckGoSearchError("Query cannot be empty")

        # Rate limiting
        self._rate_limit_check()

        # Prepare request parameters
        params = {
            "q": query,
            "format": "xml",
            "region": region,
            "safesearch": safesearch,
        }

        session = self._ensure_session()

        for attempt in range(self.config.web_search_max_retries + 1):
            try:
                logger.debug(f"Searching for: {query} (attempt {attempt + 1})")

                response = session.get(
                    self.config.web_search_base_url,
                    params=params,
                    timeout=self.config.web_search_timeout,
                )

                response.raise_for_status()

                # Parse XML response
                parsed_response = self._parse_xml_response(response.text)

                logger.info(f"Search completed successfully for: {query}")
                return parsed_response

            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout for query: {query}")
                if attempt == self.config.web_search_max_retries:
                    raise DuckDuckGoSearchError(
                        f"Request timeout after {self.config.web_search_max_retries} retries"
                    ) from None

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    logger.warning("Rate limit exceeded")
                    raise DuckDuckGoSearchError("Rate limit exceeded") from e
                logger.error(f"HTTP error {e.response.status_code}: {e}")
                if attempt == self.config.web_search_max_retries:
                    raise DuckDuckGoSearchError(f"HTTP error: {e}") from e

            except requests.exceptions.RequestException as e:
                logger.error(f"Request error: {e}")
                if attempt == self.config.web_search_max_retries:
                    raise DuckDuckGoSearchError(f"Request failed: {e}") from e

            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                if attempt == self.config.web_search_max_retries:
                    raise DuckDuckGoSearchError(f"Search failed: {e}") from e

            # Wait before retry
            if attempt < self.config.web_search_max_retries:
                time.sleep(self.config.web_search_retry_delay * (2**attempt))

        raise DuckDuckGoSearchError("Search failed after all retry attempts")

    async def async_search(
        self,
        query: str,
        region: str = "us-en",
        safesearch: str = "moderate",
    ) -> dict[str, Any]:
        """
        Perform an asynchronous web search using DuckDuckGo XML API.

        Args:
            query: Search query string
            region: Search region (default: us-en)
            safesearch: Safe search level (default: moderate)

        Returns:
            Parsed search results

        Raises:
            DuckDuckGoSearchError: If search fails
            DuckDuckGoRateLimitError: If rate limit is exceeded
        """
        if not query.strip():
            raise DuckDuckGoSearchError("Query cannot be empty")

        # Rate limiting
        self._rate_limit_check()

        # Prepare request parameters
        params = {
            "q": query,
            "format": "xml",
            "region": region,
            "safesearch": safesearch,
        }

        session = await self._ensure_async_session()

        for attempt in range(self.config.web_search_max_retries + 1):
            try:
                logger.debug(
                    f"Async searching for: {query} (attempt {attempt + 1})"
                )

                async with session.get(
                    self.config.web_search_base_url,
                    params=params,
                ) as response:
                    response.raise_for_status()
                    content = await response.text()

                # Parse XML response
                parsed_response = self._parse_xml_response(content)

                logger.info(
                    f"Async search completed successfully for: {query}"
                )
                return parsed_response

            except aiohttp.ClientResponseError as e:
                if e.status == 429:
                    logger.warning("Rate limit exceeded")
                    raise DuckDuckGoSearchError("Rate limit exceeded") from e
                logger.error(f"HTTP error {e.status}: {e}")
                if attempt == self.config.web_search_max_retries:
                    raise DuckDuckGoSearchError(f"HTTP error: {e}") from e

            except aiohttp.ClientError as e:
                logger.error(f"Request error: {e}")
                if attempt == self.config.web_search_max_retries:
                    raise DuckDuckGoSearchError(f"Request failed: {e}") from e

            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                if attempt == self.config.web_search_max_retries:
                    raise DuckDuckGoSearchError(f"Search failed: {e}") from e

            # Wait before retry
            if attempt < self.config.web_search_max_retries:
                await asyncio.sleep(
                    self.config.web_search_retry_delay * (2**attempt)
                )

        raise DuckDuckGoSearchError("Search failed after all retry attempts")

    def close(self) -> None:
        """Close the client and clean up resources."""
        if self.session:
            self.session.close()
            self.session = None

        logger.info("DuckDuckGo client closed")

    async def aclose(self) -> None:
        """Close the async client and clean up resources."""
        if self.async_session:
            await self.async_session.close()
            self.async_session = None

        logger.info("DuckDuckGo async client closed")

    def __enter__(self) -> "DuckDuckGoClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

    async def __aenter__(self) -> "DuckDuckGoClient":
        """Async context manager entry."""
        return self

    async def __aexit__(
        self, exc_type: Any, exc_val: Any, exc_tb: Any
    ) -> None:
        """Async context manager exit."""
        await self.aclose()
