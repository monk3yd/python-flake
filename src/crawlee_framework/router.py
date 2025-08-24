from crawlee.crawlers import PlaywrightCrawlingContext
from crawlee.router import Router


router = Router[PlaywrightCrawlingContext]()


@router.default_handler
async def default_handler(context: PlaywrightCrawlingContext) -> None:
    context.log.info(f"default_handler processing {context.request.url} ...")

    await context.page.pause()
