from typing import AsyncGenerator, Set
from urllib.parse import urljoin, urlparse
import asyncio
from loguru import logger
from localwebpy import HttpVisitor, Webpage
import re

class Crawler:
    def __init__(
        self,
        depth: int = 2,
        concurrency: int = 3,
        timeout: int = 60,
        use_browser: bool = False,
        headless: bool = True,
    ):
        self.depth = depth
        self.concurrency = concurrency
        self.timeout = timeout
        self.visitor = HttpVisitor(concurrency=concurrency)
        self.visited_urls: Set[str] = set()
        self.base_url = ""

    async def run(self, url: str) -> AsyncGenerator[Webpage, None]:
        self.base_url = url
        self.visited_urls.clear()
        queue = [(url, 0)]
        
        while queue:
            current_url, current_depth = queue.pop(0)
            
            if current_url in self.visited_urls or current_depth > self.depth:
                continue
                
            self.visited_urls.add(current_url)
            
            try:
                webpages = await self.visitor.visit_many([current_url])
                if webpages:
                    webpage = webpages[0]
                    yield webpage
                    
                    if current_depth < self.depth:
                        new_urls = self._extract_urls(webpage.html, current_url)
                        queue.extend((url, current_depth + 1) for url in new_urls)
            except Exception as e:
                logger.error(f"Error crawling {current_url}: {e}")

    def _extract_urls(self, html: str, base_url: str) -> Set[str]:
        urls = set()
        url_pattern = re.compile(r'href=["\'](.*?)["\']')
        
        for match in url_pattern.finditer(html):
            url = match.group(1)
            absolute_url = urljoin(base_url, url)
            
            if self._is_valid_url(absolute_url):
                urls.add(absolute_url)
                
        return urls

    def _is_valid_url(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            base_parsed = urlparse(self.base_url)
            return (
                parsed.scheme in ('http', 'https') and
                parsed.netloc == base_parsed.netloc
            )
        except:
            return False 