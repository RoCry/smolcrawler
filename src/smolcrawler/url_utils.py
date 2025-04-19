from typing import Set
from urllib.parse import urlparse, urlunparse


def normalize_url(url: str) -> str:
    """Normalize a URL by removing fragments, trailing slashes, and query parameters."""
    parsed = urlparse(url)
    # Remove fragment and query
    normalized = urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path.rstrip("/"),  # Remove trailing slash
            "",  # params
            "",  # query
            "",  # fragment
        )
    )
    return normalized


def get_url_variations(url: str) -> Set[str]:
    """Get all possible variations of a URL that should be considered the same page."""
    parsed = urlparse(url)
    variations = set()

    # Base URL without fragment and query
    base_url = normalize_url(url)
    variations.add(base_url)

    # Add variation with trailing slash only if the original path doesn't end with a slash
    if not parsed.path.endswith("/"):
        variations.add(base_url + "/")

    return variations


def is_similar_url(url1: str, url2: str) -> bool:
    """Check if two URLs point to the same page by comparing their normalized forms."""
    return normalize_url(url1) == normalize_url(url2)
