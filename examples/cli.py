import fire
from smolcrawler import Crawler


async def main(
    url: str,
    depth: int = 1,
    concurrency: int = 2,
    timeout: int = 15,
    url_prefix: str = None,
    filter_regex: str = None,
    truncate: int = 200,
    skip_url: bool = False,
    limit: int = -1,
):
    crawler = Crawler(
        depth=depth,
        concurrency=concurrency,
        timeout=timeout,
        url_prefix=url_prefix,
        filter_regex=filter_regex,
        limit=limit,
    )
    async for webpage in crawler.run(url):
        content_length = len(webpage.content) if webpage.content else 0
        html_length = len(webpage.html) if webpage.html else 0
        print(f"+++ {content_length}/{html_length} {webpage.title}: {webpage.url}")


if __name__ == "__main__":
    fire.Fire(main)
