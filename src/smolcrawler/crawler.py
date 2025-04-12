import re
from typing import AsyncGenerator, List, Literal, Set, Tuple

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
        limit: int = -1,
    ):
        self.depth = depth
        self.concurrency = concurrency
        self.timeout = timeout
        self.url_prefix = url_prefix
        self.filter_regex = re.compile(filter_regex) if filter_regex else None
        self.limit = limit
        self._setup_visitor(visitor)
        self.visited_urls: Set[str] = set()
        self.base_url = ""

        logger.info(
            f"Initialized crawler with depth={depth}, concurrency={concurrency}, visitor={visitor}, limit={limit}"
        )
        if url_prefix:
            logger.info(f"URL prefix filter: {url_prefix}")
        if filter_regex:
            logger.info(f"URL regex filter: {filter_regex}")

    def _setup_visitor(self, visitor: Literal["browser", "headless", "http"]) -> None:
        match visitor:
            case "browser":
                self.visitor = BrowserVisitor(
                    concurrency=self.concurrency, headless=False
                )
            case "headless":
                self.visitor = BrowserVisitor(
                    concurrency=self.concurrency, headless=True
                )
            case "http":
                self.visitor = HttpVisitor(concurrency=self.concurrency)

    def _should_skip_url(self, url: str, depth: int) -> bool:
        if url in self.visited_urls:
            logger.debug(f"Skipping already visited URL: {url}")
            return True

        if depth > self.depth:
            logger.debug(f"Skipping URL at depth {depth} > {self.depth}: {url}")
            return True

        return False

    async def _crawl_page(self, url: str) -> Webpage | None:
        try:
            webpages = await self.visitor.visit_many([url])
            return webpages[0] if webpages else None
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            return None

    def _get_next_urls(
        self, webpage: Webpage, current_url: str, current_depth: int
    ) -> List[Tuple[str, int]]:
        new_urls = extract_urls(webpage.html, current_url)
        valid_urls = {
            url
            for url in new_urls
            if is_valid_url(url, self.url_prefix, self.filter_regex)
        }
        logger.debug(f"Found {len(valid_urls)} valid URLs to crawl from {current_url}")
        return [(url, current_depth + 1) for url in valid_urls]

    async def run(self, url: str) -> AsyncGenerator[Webpage, None]:
        self.base_url = url
        if self.url_prefix is None:
            self.url_prefix = get_default_url_prefix(url)
            logger.info(f"Using default URL prefix: {self.url_prefix}")

        self.visited_urls.clear()
        queue = [(url, 0)]
        total_pages = 0

        while queue and (self.limit == -1 or total_pages < self.limit):
            current_url, current_depth = queue.pop(0)

            if self._should_skip_url(current_url, current_depth):
                continue

            self.visited_urls.add(current_url)
            total_pages += 1
            logger.info(
                f"Crawling [{total_pages}] {current_url} (depth: {current_depth})"
            )

            webpage = await self._crawl_page(current_url)
            if webpage:
                yield webpage

                if current_depth < self.depth:
                    next_urls = self._get_next_urls(webpage, current_url, current_depth)
                    queue.extend(next_urls)

        logger.info(f"Crawling completed. Total pages visited: {total_pages}")
