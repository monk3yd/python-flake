import asyncio
from camoufox.async_api import AsyncCamoufox

async def main():
    async with AsyncCamoufox() as browser:
        page = await browser.new_page()
        await page.goto("https://example.com")


if __name__ == "__main__":
    asyncio.run(main())
