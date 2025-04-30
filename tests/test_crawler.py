from unittest.mock import AsyncMock, MagicMock

import pytest
from localwebpy import Webpage
from smolcrawler.crawler import Crawler


@pytest.fixture
def mock_webpage():
    webpage = MagicMock(spec=Webpage)
    webpage.content = "test content"
    webpage.html = '<a href="https://example.com/page1">Link1</a><a href="https://example.com/page2">Link2</a>'
    return webpage


@pytest.fixture
def mock_visitor():
    visitor = AsyncMock()
    return visitor


@pytest.fixture
def crawler(mock_visitor):
    return Crawler(
        depth=2,
        concurrency=3,
        timeout=60,
        url_prefix="https://example.com",
        visitor=mock_visitor,
    )


@pytest.mark.asyncio
async def test_crawler_skips_visited_urls(crawler, mock_webpage, mock_visitor):
    # Setup
    mock_visitor.visit_many.return_value = [mock_webpage]
    url = "https://example.com/page"

    # First visit
    pages = []
    async for page in crawler.run(url):
        pages.append(page)

    assert len(pages) == 1
    assert url in crawler.visited_urls

    # Second visit with same URL
    pages = []
    async for page in crawler.run(url):
        pages.append(page)

    assert len(pages) == 0  # Should skip the URL


@pytest.mark.asyncio
async def test_crawler_skips_similar_urls(crawler, mock_webpage, mock_visitor):
    # Setup
    mock_visitor.visit_many.return_value = [mock_webpage]
    base_url = "https://example.com/page"
    similar_urls = [
        base_url,
        base_url + "/",
        base_url + "#section",
        base_url + "?param=value",
    ]

    # Visit first URL
    pages = []
    async for page in crawler.run(similar_urls[0]):
        pages.append(page)

    assert len(pages) == 1

    # Try visiting similar URLs
    for url in similar_urls[1:]:
        pages = []
        async for page in crawler.run(url):
            pages.append(page)
        assert len(pages) == 0  # Should skip all similar URLs


@pytest.mark.asyncio
async def test_crawler_respects_depth(crawler, mock_webpage, mock_visitor):
    # Setup
    mock_visitor.visit_many.return_value = [mock_webpage]
    url = "https://example.com/page"

    # Set depth to 1
    crawler.depth = 1

    # Run crawler
    pages = []
    async for page in crawler.run(url):
        pages.append(page)

    # Should only visit the initial page, not follow links
    assert len(pages) == 1
    assert len(crawler.visited_urls) == 1
