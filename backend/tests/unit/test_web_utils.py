"""
Unit tests for web_utils module
"""

import pytest
import asyncio
from unittest.mock import patch, Mock
from app.utils.web_utils import fetch_web_content, validate_url, _parse_html_content


class TestUrlValidation:
    """Test URL validation functionality"""

    def test_valid_urls(self):
        """Test that valid URLs are correctly identified"""
        valid_urls = [
            "https://www.example.com",
            "http://example.com",
            "https://subdomain.example.com/path",
            "https://example.com:8080/path?query=value",
            "ftp://example.com",
        ]

        for url in valid_urls:
            assert validate_url(url), f"URL should be valid: {url}"

    def test_invalid_urls(self):
        """Test that invalid URLs are correctly identified"""
        invalid_urls = [
            "example.com",  # Missing scheme
            "not-a-url",
            "",
            None,
            "://example.com",  # Missing scheme
            "http://",  # Missing domain
        ]

        for url in invalid_urls:
            assert not validate_url(url), f"URL should be invalid: {url}"


class TestHtmlParsing:
    """Test HTML content parsing functionality"""

    def test_basic_html_parsing(self):
        """Test parsing of basic HTML content"""
        html = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Main Heading</h1>
                <p>This is a paragraph with useful content.</p>
                <div>Some additional text in a div.</div>
            </body>
        </html>
        """

        result = _parse_html_content(html, "test-url")

        assert result["title"] == "Test Page"
        assert "Main Heading" in result["text"]
        assert "This is a paragraph with useful content." in result["text"]
        assert "Some additional text in a div." in result["text"]

    def test_html_filtering(self):
        """Test that unwanted HTML elements are filtered out"""
        html = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <script>alert('unwanted script');</script>
                <style>body { color: red; }</style>
                <nav>Navigation menu</nav>
                <header>Header content</header>
                <footer>Footer content</footer>
                <p>Important content that should be kept.</p>
            </body>
        </html>
        """

        result = _parse_html_content(html, "test-url")

        # Should include important content
        assert "Important content that should be kept." in result["text"]

        # Should exclude unwanted elements
        assert "alert('unwanted script')" not in result["text"]
        assert "color: red" not in result["text"]
        assert "Navigation menu" not in result["text"]
        assert "Header content" not in result["text"]
        assert "Footer content" not in result["text"]

    def test_content_length_truncation(self):
        """Test that very long content is properly truncated"""
        # Create content longer than MAX_CONTENT_LENGTH (20000 chars)
        long_content = "A" * 25000
        html = f"<html><body><p>{long_content}</p></body></html>"

        result = _parse_html_content(html, "test-url")

        # Should be truncated
        assert (
            len(result["text"]) <= 20030
        )  # MAX_CONTENT_LENGTH + buffer for truncation message
        assert "[Content truncated]" in result["text"]


class TestWebContentFetching:
    """Test web content fetching functionality"""

    @pytest.mark.asyncio
    async def test_invalid_url_handling(self):
        """Test handling of invalid URLs"""
        result = await fetch_web_content("not-a-valid-url")

        assert result["success"] is False
        assert "URL must include scheme" in result["error"]
        assert result["content"] == ""

    @pytest.mark.asyncio
    async def test_empty_url_handling(self):
        """Test handling of empty/None URLs"""
        result = await fetch_web_content("")
        assert result["success"] is False
        assert "Invalid URL provided" in result["error"]

        result = await fetch_web_content(None)
        assert result["success"] is False
        assert "Invalid URL provided" in result["error"]

    @pytest.mark.asyncio
    async def test_successful_fetch_mock(self):
        """Test successful content fetching with mocked response"""
        mock_html = """
        <html>
            <head><title>Mock Page</title></head>
            <body>
                <h1>Test Content</h1>
                <p>This is mock content for testing.</p>
            </body>
        </html>
        """

        # Mock the synchronous fetch function
        with patch("app.utils.web_utils._fetch_url_sync") as mock_fetch:
            mock_fetch.return_value = {
                "success": True,
                "html": mock_html,
                "status_code": 200,
            }

            result = await fetch_web_content("https://example.com")

            assert result["success"] is True
            assert "Test Content" in result["content"]
            assert "This is mock content for testing." in result["content"]
            assert result["metadata"]["title"] == "Mock Page"
            assert result["metadata"]["status_code"] == 200
            assert result["metadata"]["url"] == "https://example.com"

    @pytest.mark.asyncio
    async def test_http_error_handling(self):
        """Test handling of HTTP errors"""
        with patch("app.utils.web_utils._fetch_url_sync") as mock_fetch:
            mock_fetch.return_value = {
                "success": False,
                "error": "HTTP error 404: Not Found",
                "status_code": 404,
            }

            result = await fetch_web_content("https://example.com/nonexistent")

            assert result["success"] is False
            assert "HTTP error 404" in result["error"]
            assert result["metadata"]["status_code"] == 404

    @pytest.mark.asyncio
    async def test_connection_error_handling(self):
        """Test handling of connection errors"""
        with patch("app.utils.web_utils._fetch_url_sync") as mock_fetch:
            mock_fetch.return_value = {
                "success": False,
                "error": "Connection error: Unable to connect to the URL",
                "status_code": None,
            }

            result = await fetch_web_content("https://nonexistent-domain-12345.com")

            assert result["success"] is False
            assert "Connection error" in result["error"]
            assert result["metadata"]["status_code"] is None


if __name__ == "__main__":
    pytest.main([__file__])
