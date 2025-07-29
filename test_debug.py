import asyncio
import traceback

from smolcrawler import Crawler


async def main():
    url = "https://www.sec.gov/Archives/edgar/data/2066899/000121390025064165/ea0237719-04.htm"
    crawler = Crawler(depth=1, concurrency=2)

    try:
        async for webpage in crawler.run(url):
            print(f"Got webpage: {webpage.title}")
    except Exception as e:
        print(f"Exception type: {type(e)}")
        print(f"Exception: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
