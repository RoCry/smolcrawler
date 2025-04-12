import re
from typing import AsyncGenerator, Literal, Set

from localwebpy import BrowserVisitor, HttpVisitor, Webpage
from loguru import logger

from .utils import extract_urls, get_default_url_prefix, is_valid_url


class Crawler:
    def __init__(
        self,
        depth: int = 2,
        concurrency: int = 3,
        timeout: int = 60,
        url_prefix: str | None = None,
        filter_regex: str | None = None,
        visitor: Literal["browser", "headless", "http"] = "http",
    ):
        self.depth = depth
        self.concurrency = concurrency
        self.timeout = timeout
        self.url_prefix = url_prefix
        self.filter_regex = re.compile(filter_regex) if filter_regex else None
        match visitor:
            case "browser":
                self.visitor = BrowserVisitor(concurrency=concurrency, headless=False)
            case "headless":
                self.visitor = BrowserVisitor(concurrency=concurrency, headless=True)
            case "http":
                self.visitor = HttpVisitor(concurrency=concurrency)
        self.visited_urls: Set[str] = set()
        self.base_url = ""

        logger.info(
            f"Initialized crawler with depth={depth}, concurrency={concurrency}, visitor={visitor}"
        )
        if url_prefix:
            logger.info(f"URL prefix filter: {url_prefix}")
        if filter_regex:
            logger.info(f"URL regex filter: {filter_regex}")

    async def run(self, url: str) -> AsyncGenerator[Webpage, None]:
        self.base_url = url
        if self.url_prefix is None:
            self.url_prefix = get_default_url_prefix(url)
            logger.info(f"Using default URL prefix: {self.url_prefix}")

        self.visited_urls.clear()
        queue = [(url, 0)]
        total_pages = 0

        while queue:
            current_url, current_depth = queue.pop(0)

            if current_url in self.visited_urls:
                logger.debug(f"Skipping already visited URL: {current_url}")
                continue

            if current_depth > self.depth:
                logger.debug(
                    f"Skipping URL at depth {current_depth} > {self.depth}: {current_url}"
                )
                continue

            self.visited_urls.add(current_url)
            total_pages += 1
            logger.info(
                f"Crawling [{total_pages}] {current_url} (depth: {current_depth})"
            )

            try:
                webpages = await self.visitor.visit_many([current_url])
                if webpages:
                    webpage = webpages[0]
                    yield webpage

                    if current_depth < self.depth:
                        new_urls = extract_urls(webpage.html, current_url)
                        valid_urls = {
                            url
                            for url in new_urls
                            if is_valid_url(url, self.url_prefix, self.filter_regex)
                        }
                        queue.extend((url, current_depth + 1) for url in valid_urls)
                        logger.debug(
                            f"Found {len(valid_urls)} valid URLs to crawl from {current_url}"
                        )
            except Exception as e:
                logger.error(f"Error crawling {current_url}: {e}")

        logger.info(f"Crawling completed. Total pages visited: {total_pages}")
