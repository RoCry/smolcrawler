from typing import AsyncGenerator, Set, Literal
from urllib.parse import urljoin, urlparse
from loguru import logger
from localwebpy import HttpVisitor, Webpage, BrowserVisitor
import re

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

    async def run(self, url: str) -> AsyncGenerator[Webpage, None]:
        self.base_url = url
        if self.url_prefix is None:
            # Default: use the initial URL as prefix
            parsed = urlparse(url)
            self.url_prefix = f"{parsed.scheme}://{parsed.netloc}"
        
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
            
            # Basic URL validation
            if parsed.scheme not in ('http', 'https'):
                return False
                
            # Check prefix if specified
            if self.url_prefix and not url.startswith(self.url_prefix):
                return False
                
            # Check regex if specified
            if self.filter_regex and not self.filter_regex.search(url):
                return False
                
            return True
        except:
            return False 