import re
from typing import Set
from urllib.parse import urljoin, urlparse

from loguru import logger


def extract_urls(html: str, base_url: str) -> Set[str]:
    urls = set()
    url_pattern = re.compile(r'href=["\'](.*?)["\']')

    for match in url_pattern.finditer(html):
        url = match.group(1)
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
