import re
from typing import Set
from urllib.parse import urljoin, urlparse

from loguru import logger


def extract_urls(html: str, base_url: str) -> Set[str]:
    urls = set()
    # Match href attributes in anchor tags, ignoring case
    url_pattern = re.compile(r'<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    
    # Parse base URL to handle relative paths correctly
    base_parsed = urlparse(base_url)
    base_path = base_parsed.path.rstrip('/')
    
    for match in url_pattern.finditer(html):
        url = match.group(1)
        # Skip empty URLs, anchors, and javascript
        if not url or url.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue
            
        # Handle protocol-relative URLs (//example.com/path)
        if url.startswith('//'):
            url = f"{base_parsed.scheme}:{url}"
            
        # Handle root-relative URLs (/path)
        if url.startswith('/'):
            absolute_url = f"{base_parsed.scheme}://{base_parsed.netloc}{url}"
        else:
            # Handle relative paths (path, ./path, ../path)
            absolute_url = urljoin(base_url, url)
            
        urls.add(absolute_url)
        
    return urls


def is_valid_url(
    url: str,
    url_prefix: str | None = None,
    filter_regex: re.Pattern | None = None,
) -> bool:
    try:
        parsed = urlparse(url)
        
        # Basic URL validation
        if parsed.scheme not in ("http", "https"):
            return False
            
        # Get the path without query parameters
        path = parsed.path.split("?")[0]
        
        # Allow URLs with no extension or HTML-like extensions
        if path and "." in path:
            ext = path.split(".")[-1].lower()
            if ext not in ["", "html", "htm", "php", "asp", "aspx", "jsp"]:
                return False
            
        # Check prefix if specified
        if url_prefix and not url.startswith(url_prefix):
            return False
            
        # Check regex if specified
        if filter_regex and not filter_regex.search(url):
            return False
            
        return True
    except Exception as e:
        logger.error(f"Error validating URL {url}: {e}")
        return False


def get_default_url_prefix(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"
