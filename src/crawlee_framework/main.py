import asyncio
import random

from crawlee.browsers import BrowserPool
from crawlee.crawlers import BasicCrawlingContext, PlaywrightCrawler, PlaywrightCrawlingContext, PlaywrightPreNavCrawlingContext
from crawlee.sessions import Session, SessionPool
from crawlee.storages import Dataset
from crawlee import Request, ConcurrencySettings
from crawlee.proxy_configuration import ProxyConfiguration

from datetime import timedelta
from itertools import count
from typing import Callable, Union

from camoufox_plugin import CamoufoxPlugin
from router import router
from settings import settings


async def main() -> None:

    # NOTE:--- Crawlee configurations ---
    ABORT_ON_ERROR = False
    MAX_CONCURRENCY = 1
    # MAX_REQUESTS_PER_CRAWL = 500
    MAX_REQUEST_RETRIES = 1
    MAX_TASKS_PER_MINUTE = 140
    REQUEST_TIMEOUT = 60 
    RETRY_ON_BLOCKED = True
    POOLSIZE = 1

    # Randomize proxy session generation
    base_number = random.randint(1, 999999)
    max_range = base_number + POOLSIZE

    # Generate as many proxies as sessions needed
    # datacenter_proxy_urls = []
    # for proxy_session_id in range(base_number, max_range+1):
    #     proxy_session_url = ""
    #     datacenter_proxy_urls.append(proxy_session_url)

    proxy_configuration = ProxyConfiguration(
        tiered_proxy_urls=[
            # No proxy tier. (Not needed, but optional in case you do not want to use any proxy on lowest tier.)
            [None],

            # lower tier, cheaper, preferred as long as they work
            # datacenter_proxy_urls

            # higher tier, more expensive, used as a fallback
            # ['http://expensive-residential-proxy-1.com/', 'http://expensive-residential-proxy-2.com/'],
        ]
    )

    concurrency_settings = ConcurrencySettings()
    concurrency_settings.max_tasks_per_minute = MAX_TASKS_PER_MINUTE
    concurrency_settings.max_concurrency = MAX_CONCURRENCY


    crawler = PlaywrightCrawler(
        request_handler=router,
        request_handler_timeout=timedelta(seconds=REQUEST_TIMEOUT),
        concurrency_settings=concurrency_settings,
        retry_on_blocked=RETRY_ON_BLOCKED,
        max_request_retries=MAX_REQUEST_RETRIES,
        use_session_pool=True,
        max_session_rotations=0,
        session_pool=SessionPool(
            max_pool_size=POOLSIZE,
            create_session_function=create_session_function()
        ),
        proxy_configuration=proxy_configuration,
        abort_on_error=ABORT_ON_ERROR,
        additional_http_error_status_codes=[404],
        browser_pool=BrowserPool(
            operation_timeout=timedelta(seconds=REQUEST_TIMEOUT),
            plugins=[CamoufoxPlugin()]
        )
    )

    @crawler.error_handler
    async def error_handler(context: Union[PlaywrightCrawlingContext, BasicCrawlingContext], error: Exception) -> Union[Request, None]:
        context.log.warning(f"error_handler retry {context.request.retry_count} error {str(error)} processing url {context.request.url} ...")


    @crawler.failed_request_handler
    async def failed_request_handler(context: Union[PlaywrightCrawlingContext, BasicCrawlingContext], error: Exception) -> None:
        context.log.error(f"failed_request_handler error {str(error)} processing url {context.request.url} ...")

        failed = {
            "id": context.request.id,
            "url": context.request.url,
            "error": str(error),
            "request": context.request.model_dump()
        }
        dataset = await Dataset.open(name="errors")
        await dataset.push_data(failed)


    @crawler.pre_navigation_hook
    async def navigation_hook(context: PlaywrightPreNavCrawlingContext) -> None:
        context.log.info(f'Navigating to {context.request.url} ...')

        # Block all requests to URLs that include `adsbygoogle.js` and also all defaults.
        # default blocks: ['.css', '.webp', '.jpg', '.jpeg', '.png', '.svg', '.gif', '.woff', '.pdf', '.zip']
        # await context.block_requests(url_patterns=['.jpg', '.jpeg', '.png', '.svg'], extra_url_patterns=['adsbygoogle.js'])
        await context.block_requests(extra_url_patterns=['adsbygoogle.js'])


    init = Request.from_url(
        url="https://www.example.com",
        method="GET",
        session_id=str(1),
    )
    await crawler.run([init])
    # await crawler.export_data_csv(path="results.csv", dataset_name=settings.SPIDER_NAME)


# Define a function for creating sessions with simple logic for unique `id` generation.
# This is necessary if you need to specify a particular session for the first request,
# for example during authentication
def create_session_function() -> Callable[[], Session]:
    counter = count()

    def create_session() -> Session:
        return Session(
            id=str(next(counter)+1),
            max_usage_count=999_999,
            max_age=timedelta(hours=999_999),
            max_error_score=100,
            blocked_status_codes=[403],
        )

    return create_session


if __name__ == "__main__":
    asyncio.run(main())
