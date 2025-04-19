import re
from typing import Set
from urllib.parse import urlparse

from loguru import logger


def extract_urls(html: str, base_url: str) -> Set[str]:
    urls = set()
    url_pattern = re.compile(r'<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)

    # Parse base URL
    base_parsed = urlparse(base_url)
    base_path = base_parsed.path.rstrip("/")

    for match in url_pattern.finditer(html):
        url = match.group(1)

        # Skip invalid URLs
        if not url or url.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue

        # Handle absolute URLs
        if url.startswith(("http://", "https://")):
            urls.add(url)
            continue

        # Handle different URL types
        if url.startswith("/"):
            # Root-relative URL
            absolute_url = f"{base_parsed.scheme}://{base_parsed.netloc}{url}"
        elif url.startswith("../"):
            # Parent directory
            parent_count = url.count("../")
            url = url[3 * parent_count :]  # Remove ../ prefixes
            path_parts = base_path.split("/")
            if len(path_parts) > parent_count:
                parent_path = "/".join(path_parts[:-parent_count])
            else:
                parent_path = ""
            absolute_url = (
                f"{base_parsed.scheme}://{base_parsed.netloc}/{parent_path}/{url}"
            )
        else:
            # Current directory or relative path
            if url.startswith("./"):
                url = url[2:]  # Remove ./ prefix
            absolute_url = (
                f"{base_parsed.scheme}://{base_parsed.netloc}/{base_path}/{url}"
            )

        # Clean up any double slashes in the path while preserving the scheme
        absolute_url = re.sub(r"(?<!:)//+", "/", absolute_url)
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
