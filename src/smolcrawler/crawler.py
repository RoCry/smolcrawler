import re
from typing import AsyncGenerator, List, Set, Tuple

from localwebpy import SmartVisitor, Visitor, Webpage
from loguru import logger

from .content_detector import ContentDetector, HashBasedDetector
from .utils import extract_urls, get_default_url_prefix, is_valid_url


class Crawler:
    def __init__(
        self,
        depth: int = 2,
        concurrency: int = 3,
        timeout: int = 60,
        url_prefix: str | None = None,
        filter_regex: str | None = None,
        limit: int = 100,
        content_detector: ContentDetector | None = None,
        visitor: Visitor
        | None = None,  # if provided, will use this visitor instead of the default one
    ):
        self.depth = depth
        self.concurrency = concurrency
        self.timeout = timeout
        self.url_prefix = url_prefix
        self.filter_regex = re.compile(filter_regex) if filter_regex else None
        self.limit = limit
        self.visitor = visitor or SmartVisitor(concurrency=concurrency, timeout=timeout)
        self.visited_urls: Set[str] = set()
        self.content_detector = content_detector or HashBasedDetector()
        self.base_url = ""

        logger.info(
            f"Initialized crawler with depth={depth}, concurrency={concurrency}, limit={limit}"
        )
        if url_prefix:
            logger.info(f"URL prefix filter: {url_prefix}")
        if filter_regex:
            logger.info(f"URL regex filter: {filter_regex}")

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
        self.content_detector.clear()
        queue = [(url, 0)]
        total_pages = 0
        skipped_pages = 0

        while queue and (self.limit == -1 or total_pages - skipped_pages < self.limit):
            # Process URLs in batches up to concurrency limit
            batch_size = min(self.concurrency, len(queue))
            current_batch = [queue.pop(0) for _ in range(batch_size)]

            # Filter out URLs that should be skipped
            urls_to_crawl = []
            for current_url, current_depth in current_batch:
                if not self._should_skip_url(current_url, current_depth):
                    urls_to_crawl.append((current_url, current_depth))
                    self.visited_urls.add(current_url)
                    total_pages += 1
                    logger.info(
                        f"Queuing [{total_pages}] {current_url} (depth: {current_depth})"
                    )

            if not urls_to_crawl:
                continue

            # Batch visit URLs
            webpages = await self.visitor.visit_many([url for url, _ in urls_to_crawl])

            # Process results
            for webpage, (current_url, current_depth) in zip(webpages, urls_to_crawl):
                if webpage:
                    content = webpage.content
                    if not content:
                        logger.warning(f"No content found for {current_url}")
                        skipped_pages += 1
                        continue
                    if self.content_detector.is_duplicate(content):
                        skipped_pages += 1
                        continue
                    self.content_detector.add_content(content)

                    yield webpage

                    if current_depth < self.depth:
                        next_urls = self._get_next_urls(
                            webpage, current_url, current_depth
                        )
                        queue.extend(next_urls)

        logger.info(
            f"Crawling completed. Total pages: {total_pages}, Skipped: {skipped_pages}"
        )
