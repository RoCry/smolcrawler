# Introduction
This is a simple small crawler for fetch a webpage and everything it links to.
## Features
- Returns in markdown format.
- Regex to match the url to crawl
- Only fetch the urls that have same prefix with the initial url by default

## Usage
```bash
# this will fetch the url and everything it links to, and output to stdout
uv run src/crawler.py --url https://swiftpackageindex.com/grpc/grpc-swift-protobuf/1.1.0/documentation/grpcprotobuf
```

```python
from smolcrawler import Crawler

crawler = Crawler(depth=2, concurrency=3, timeout=60)
async for page in crawler.run(url="https://swiftpackageindex.com/grpc/grpc-swift-protobuf/1.1.0/documentation/grpcprotobuf"):
    print(page)
```

# Tech Stack 

- Only supports python >= 3.12
- Only use uv to manage dependencies
- Use httpx to fetch the webpage
- `from loguru import logger` to log the messages


## Third Party Libraries

### localwebpy
used to visit pages and get the markdown content of them, demo code:
```python
# use headless browser if needed(e.g. async content, cloudflare protection), or use http to visit pages
visitor = BrowserVisitor(headless=headless, concurrency=concurrency) if use_browser else HttpVisitor(concurrency=concurrency)
# async def visit_many(self, url_or_webpages: List[str | Webpage]) -> List[Webpage]:
# and then `visitor.visit_many(urls)`
```