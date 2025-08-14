"""
Unit tests for DuckDuckGo client.

Tests cover all functionality including error handling, rate limiting,
session management, and XML parsing.
"""

import time
from unittest.mock import AsyncMock, Mock, patch

import aiohttp
import pytest
import requests

from core.config import AppConfig
from integrations.search.duckduckgo_client import DuckDuckGoClient
from integrations.search.exceptions import DuckDuckGoSearchError


class TestDuckDuckGoClient:
    """Test suite for DuckDuckGo client."""

    @pytest.fixture
    def mock_config(self) -> Mock:
        """Create a mock configuration for testing."""
        config = Mock(spec=AppConfig)
        config.web_search_user_agent = "Test User Agent"
        config.web_search_timeout = 30
        config.web_search_max_retries = 3
        config.web_search_retry_delay = 1.0
        config.web_search_rate_limit_delay = 1.0
        config.web_search_base_url = "https://api.duckduckgo.com/"
        return config

    @pytest.fixture
    def client(self, mock_config: Mock) -> DuckDuckGoClient:
        """Create a DuckDuckGo client instance for testing."""
        return DuckDuckGoClient(config=mock_config)

    @pytest.fixture
    def sample_xml_response(self) -> str:
        """Sample XML response for testing."""
        return """<?xml version="1.0" encoding="UTF-8"?>
        <DuckDuckGo query="test query">
            <Abstract>Test abstract text</Abstract>
            <AbstractURL>https://example.com/abstract</AbstractURL>
            <Results>
                <Result>
                    <Title>Test Result 1</Title>
                    <FirstURL>https://example.com/1</FirstURL>
                    <Text>This is a test result snippet</Text>
                </Result>
                <Result>
                    <Title>Test Result 2</Title>
                    <FirstURL>https://example.com/2</FirstURL>
                    <Text>Another test result snippet</Text>
                </Result>
            </Results>
        </DuckDuckGo>"""

    def test_init(self, mock_config: Mock) -> None:
        """Test client initialization."""
        client = DuckDuckGoClient(config=mock_config)

        assert client.config == mock_config
        assert client.session is None
        assert client.async_session is None
        assert client._last_request_time == 0.0

    def test_ensure_session(self, client: DuckDuckGoClient) -> None:
        """Test session creation and reuse."""
        # First call should create session
        session1 = client._ensure_session()
        assert session1 is not None
        assert (
            session1.headers["User-Agent"]
            == client.config.web_search_user_agent
        )

        # Second call should return same session
        session2 = client._ensure_session()
        assert session2 is session1

    @pytest.mark.asyncio
    async def test_ensure_async_session(
        self, client: DuckDuckGoClient
    ) -> None:
        """Test async session creation and reuse."""
        # First call should create session
        session1 = await client._ensure_async_session()
        assert session1 is not None
        assert (
            session1.headers["User-Agent"]
            == client.config.web_search_user_agent
        )

        # Second call should return same session
        session2 = await client._ensure_async_session()
        assert session2 is session1

    def test_rate_limit_check(self, client: DuckDuckGoClient) -> None:
        """Test rate limiting functionality."""
        # Set last request time to simulate recent request
        client._last_request_time = time.time()

        # Should not sleep if enough time has passed
        client._rate_limit_check()

        # Should sleep if not enough time has passed
        with patch("time.sleep") as mock_sleep:
            client._rate_limit_check()
            mock_sleep.assert_called_once()

    def test_parse_xml_response_valid(
        self, client: DuckDuckGoClient, sample_xml_response: str
    ) -> None:
        """Test parsing valid XML response."""
        result = client._parse_xml_response(sample_xml_response)

        assert result["query"] == "test query"
        assert result["abstract"] == "Test abstract text"
        assert result["abstract_url"] == "https://example.com/abstract"
        assert len(result["results"]) == 2

        # Check first result
        first_result = result["results"][0]
        assert first_result["title"] == "Test Result 1"
        assert first_result["url"] == "https://example.com/1"
        assert first_result["snippet"] == "This is a test result snippet"

    def test_parse_xml_response_invalid_xml(
        self, client: DuckDuckGoClient
    ) -> None:
        """Test parsing invalid XML response."""
        with pytest.raises(
            DuckDuckGoSearchError, match="Invalid XML response"
        ):
            client._parse_xml_response("invalid xml content")

    def test_parse_xml_response_missing_elements(
        self, client: DuckDuckGoClient
    ) -> None:
        """Test parsing XML with missing elements."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<DuckDuckGo query="test">
    <Results>
        <Result>
            <Title>Test</Title>
        </Result>
    </Results>
</DuckDuckGo>"""

        result = client._parse_xml_response(xml_content)
        assert result["query"] == "test"
        assert result["abstract"] == ""
        assert result["abstract_url"] == ""
        assert len(result["results"]) == 1
        assert result["results"][0]["title"] == "Test"
        # The XML parsing only adds fields that exist, so url and snippet won't be present
        assert "url" not in result["results"][0]
        assert "snippet" not in result["results"][0]

    def test_search_empty_query(self, client: DuckDuckGoClient) -> None:
        """Test search with empty query."""
        with pytest.raises(
            DuckDuckGoSearchError, match="Query cannot be empty"
        ):
            client.search("")

    def test_search_whitespace_query(self, client: DuckDuckGoClient) -> None:
        """Test search with whitespace-only query."""
        with pytest.raises(
            DuckDuckGoSearchError, match="Query cannot be empty"
        ):
            client.search("   ")

    @patch("requests.Session")
    def test_search_success(
        self,
        mock_session_class: Mock,
        client: DuckDuckGoClient,
        sample_xml_response: str,
    ) -> None:
        """Test successful search."""
        # Setup mock session
        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = sample_xml_response
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        # Mock rate limiting
        with patch.object(client, "_rate_limit_check"):
            result = client.search("test query")

        # Verify session was created
        mock_session_class.assert_called_once()
        mock_session.headers.update.assert_called_once()

        # Verify request was made
        mock_session.get.assert_called_once()
        call_args = mock_session.get.call_args
        assert call_args[0][0] == client.config.web_search_base_url

        # Verify response parsing
        assert result["query"] == "test query"
        assert len(result["results"]) == 2

    @patch("requests.Session")
    def test_search_timeout_retry(
        self, mock_session_class: Mock, client: DuckDuckGoClient
    ) -> None:
        """Test search with timeout and retry."""
        # Setup mock session
        mock_session = Mock()
        mock_session.get.side_effect = requests.exceptions.Timeout(
            "Request timeout"
        )
        mock_session_class.return_value = mock_session

        # Mock rate limiting and sleep
        with patch.object(client, "_rate_limit_check"), patch("time.sleep"):
            with pytest.raises(
                DuckDuckGoSearchError, match="Request timeout after 3 retries"
            ):
                client.search("test query")

        # Verify retries were attempted
        assert mock_session.get.call_count == 4  # Initial + 3 retries

    @patch("requests.Session")
    def test_search_rate_limit_error(
        self, mock_session_class: Mock, client: DuckDuckGoClient
    ) -> None:
        """Test search with rate limit error."""
        # Setup mock session
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = (
            requests.exceptions.HTTPError(
                "Rate limit exceeded", response=mock_response
            )
        )
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        # Mock rate limiting
        with patch.object(client, "_rate_limit_check"):
            with pytest.raises(
                DuckDuckGoSearchError, match="Rate limit exceeded"
            ):
                client.search("test query")

    @patch("requests.Session")
    def test_search_http_error(
        self, mock_session_class: Mock, client: DuckDuckGoClient
    ) -> None:
        """Test search with HTTP error."""
        # Setup mock session
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = (
            requests.exceptions.HTTPError(
                "Server error", response=mock_response
            )
        )
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        # Mock rate limiting and sleep
        with patch.object(client, "_rate_limit_check"), patch("time.sleep"):
            with pytest.raises(DuckDuckGoSearchError, match="HTTP error"):
                client.search("test query")

    @patch("requests.Session")
    def test_search_request_exception(
        self, mock_session_class: Mock, client: DuckDuckGoClient
    ) -> None:
        """Test search with request exception."""
        # Setup mock session
        mock_session = Mock()
        mock_session.get.side_effect = requests.exceptions.ConnectionError(
            "Connection failed"
        )
        mock_session_class.return_value = mock_session

        # Mock rate limiting and sleep
        with patch.object(client, "_rate_limit_check"), patch("time.sleep"):
            with pytest.raises(DuckDuckGoSearchError, match="Request failed"):
                client.search("test query")

    @pytest.mark.asyncio
    async def test_async_search_empty_query(
        self, client: DuckDuckGoClient
    ) -> None:
        """Test async search with empty query."""
        with pytest.raises(
            DuckDuckGoSearchError, match="Query cannot be empty"
        ):
            await client.async_search("")

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession")
    async def test_async_search_success(
        self,
        mock_session_class: Mock,
        client: DuckDuckGoClient,
        sample_xml_response: str,
    ) -> None:
        """Test successful async search."""
        # Setup mock session
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.text.return_value = sample_xml_response
        mock_response.raise_for_status.return_value = None

        # Configure the response as an async context manager
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        # Mock rate limiting
        with patch.object(client, "_rate_limit_check"):
            result = await client.async_search("test query")

        # Verify session was created
        mock_session_class.assert_called_once()

        # Verify response parsing
        assert result["query"] == "test query"
        assert len(result["results"]) == 2

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession")
    async def test_async_search_rate_limit_error(
        self, mock_session_class: Mock, client: DuckDuckGoClient
    ) -> None:
        """Test async search with rate limit error."""
        # Setup mock session
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.raise_for_status.side_effect = (
            aiohttp.ClientResponseError(
                request_info=Mock(), history=(), status=429
            )
        )

        # Configure the response as an async context manager
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        # Mock rate limiting
        with patch.object(client, "_rate_limit_check"):
            with pytest.raises(
                DuckDuckGoSearchError, match="Rate limit exceeded"
            ):
                await client.async_search("test query")

    def test_context_manager(self, client: DuckDuckGoClient) -> None:
        """Test context manager functionality."""
        with patch.object(client, "close") as mock_close:
            with client as ctx_client:
                assert ctx_client is client

            mock_close.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_context_manager(
        self, client: DuckDuckGoClient
    ) -> None:
        """Test async context manager functionality."""
        with patch.object(client, "aclose") as mock_aclose:
            async with client as ctx_client:
                assert ctx_client is client

            mock_aclose.assert_called_once()

    def test_close(self, client: DuckDuckGoClient) -> None:
        """Test client close functionality."""
        # Create a session first
        client._ensure_session()
        assert client.session is not None

        # Close client
        client.close()
        assert client.session is None

    @pytest.mark.asyncio
    async def test_aclose(self, client: DuckDuckGoClient) -> None:
        """Test async client close functionality."""
        # Create an async session first
        await client._ensure_async_session()
        assert client.async_session is not None

        # Close client
        await client.aclose()
        assert client.async_session is None

    def test_search_with_custom_parameters(
        self, client: DuckDuckGoClient
    ) -> None:
        """Test search with custom region and safesearch parameters."""
        with patch("requests.Session") as mock_session_class:
            mock_session = Mock()
            mock_response = Mock()
            mock_response.text = self._get_sample_xml_response()
            mock_response.raise_for_status.return_value = None
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session

            with patch.object(client, "_rate_limit_check"):
                client.search(
                    query="test query",
                    region="uk-en",
                    safesearch="strict",
                )

            # Verify parameters were passed correctly
            call_args = mock_session.get.call_args
            params = call_args[1]["params"]
            assert params["q"] == "test query"
            assert params["region"] == "uk-en"
            assert params["safesearch"] == "strict"

    def _get_sample_xml_response(self) -> str:
        """Helper method to provide sample XML response."""
        return """<?xml version="1.0" encoding="UTF-8"?>
        <DuckDuckGo query="test query">
            <Abstract>Test abstract text</Abstract>
            <AbstractURL>https://example.com/abstract</AbstractURL>
            <Results>
                <Result>
                    <Title>Test Result 1</Title>
                    <FirstURL>https://example.com/1</FirstURL>
                    <Text>This is a test result snippet</Text>
                </Result>
            </Results>
        </DuckDuckGo>"""
