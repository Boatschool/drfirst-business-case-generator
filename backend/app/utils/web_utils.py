"""
Web content fetching and parsing utilities for the DrFirst Business Case Generator.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup, Tag
from requests.exceptions import RequestException, Timeout, ConnectionError, HTTPError

# Set up logging
logger = logging.getLogger(__name__)

# Configuration constants
DEFAULT_TIMEOUT = 10  # seconds
MAX_CONTENT_LENGTH = 20000  # characters
USER_AGENT = "DrFirst-Business-Case-Generator/1.0"


async def fetch_web_content(url: str) -> Dict[str, Any]:
    """
    Asynchronously fetch and parse text content from a web URL.
    
    Args:
        url (str): The URL to fetch content from
        
    Returns:
        Dict[str, Any]: A dictionary containing:
            - success (bool): Whether the fetch was successful
            - content (str): The extracted text content (if successful)
            - error (str): Error message (if unsuccessful)
            - metadata (dict): Additional info like title, url, etc.
    """
    
    # Input validation
    if not url or not isinstance(url, str):
        return {
            "success": False,
            "content": "",
            "error": "Invalid URL provided",
            "metadata": {"url": url}
        }
    
    # Basic URL validation
    try:
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return {
                "success": False,
                "content": "",
                "error": "URL must include scheme (http/https) and domain",
                "metadata": {"url": url}
            }
    except Exception as e:
        return {
            "success": False,
            "content": "",
            "error": f"Invalid URL format: {str(e)}",
            "metadata": {"url": url}
        }
    
    try:
        # Use asyncio.to_thread to run the synchronous requests call asynchronously
        response = await asyncio.to_thread(_fetch_url_sync, url)
        
        if response["success"]:
            # Parse the HTML content
            parsed_content = _parse_html_content(response["html"], url)
            return {
                "success": True,
                "content": parsed_content["text"],
                "error": "",
                "metadata": {
                    "url": url,
                    "title": parsed_content["title"],
                    "content_length": len(parsed_content["text"]),
                    "status_code": response["status_code"]
                }
            }
        else:
            return {
                "success": False,
                "content": "",
                "error": response["error"],
                "metadata": {
                    "url": url,
                    "status_code": response.get("status_code")
                }
            }
            
    except Exception as e:
        logger.error(f"Unexpected error fetching content from {url}: {str(e)}")
        return {
            "success": False,
            "content": "",
            "error": f"Unexpected error: {str(e)}",
            "metadata": {"url": url}
        }


def _fetch_url_sync(url: str) -> Dict[str, Any]:
    """
    Synchronous helper function to fetch URL content.
    This is called via asyncio.to_thread for async compatibility.
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }
    
    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=DEFAULT_TIMEOUT,
            allow_redirects=True,
            stream=True  # For checking content length
        )
        
        # Check status code
        response.raise_for_status()
        
        # Check content type
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' not in content_type and 'application/xhtml' not in content_type:
            return {
                "success": False,
                "error": f"Unsupported content type: {content_type}",
                "status_code": response.status_code
            }
        
        # Get content with size limit
        content = ""
        total_size = 0
        for chunk in response.iter_content(chunk_size=8192, decode_unicode=True):
            if chunk:
                total_size += len(chunk)
                if total_size > MAX_CONTENT_LENGTH * 2:  # Allow some buffer for HTML
                    logger.warning(f"Content from {url} exceeds size limit, truncating")
                    break
                content += chunk
        
        return {
            "success": True,
            "html": content,
            "status_code": response.status_code
        }
        
    except HTTPError as e:
        return {
            "success": False,
            "error": f"HTTP error {e.response.status_code}: {str(e)}",
            "status_code": e.response.status_code if e.response else None
        }
    except ConnectionError:
        return {
            "success": False,
            "error": "Connection error: Unable to connect to the URL",
            "status_code": None
        }
    except Timeout:
        return {
            "success": False,
            "error": f"Timeout: Request took longer than {DEFAULT_TIMEOUT} seconds",
            "status_code": None
        }
    except RequestException as e:
        return {
            "success": False,
            "error": f"Request error: {str(e)}",
            "status_code": None
        }


def _parse_html_content(html: str, url: str) -> Dict[str, str]:
    """
    Parse HTML content and extract meaningful text.
    
    Args:
        html (str): Raw HTML content
        url (str): Original URL (for context)
        
    Returns:
        Dict[str, str]: Dictionary with 'text' and 'title' keys
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else "No title"
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'sidebar', 'aside']):
            element.decompose()
        
        # Extract text from meaningful elements
        text_elements = []
        
        # Priority order: main content areas first
        content_selectors = [
            'main', 'article', '[role="main"]', '.content', '#content',
            '.main-content', '.post-content', '.entry-content'
        ]
        
        main_content = None
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        # If we found main content, use that; otherwise use the whole body
        content_root = main_content if main_content else soup.find('body')
        if not content_root:
            content_root = soup
        
        # Extract text from headings and paragraphs
        for tag in content_root.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'td', 'div']):
            if isinstance(tag, Tag):
                text = tag.get_text().strip()
                if text and len(text) > 10:  # Filter out very short text snippets
                    text_elements.append(text)
        
        # Join all text elements
        full_text = '\n'.join(text_elements)
        
        # Truncate if too long
        if len(full_text) > MAX_CONTENT_LENGTH:
            full_text = full_text[:MAX_CONTENT_LENGTH] + "... [Content truncated]"
        
        return {
            "text": full_text,
            "title": title
        }
        
    except Exception as e:
        logger.error(f"Error parsing HTML content from {url}: {str(e)}")
        return {
            "text": f"Error parsing content: {str(e)}",
            "title": "Parse Error"
        }


def validate_url(url: str) -> bool:
    """
    Basic URL validation.
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if URL appears valid, False otherwise
    """
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)
    except Exception:
        return False 