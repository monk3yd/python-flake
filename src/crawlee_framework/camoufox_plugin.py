import os
from crawlee.browsers import PlaywrightBrowserPlugin, PlaywrightBrowserController
from camoufox import AsyncNewBrowser

from typing_extensions import override


class CamoufoxPlugin(PlaywrightBrowserPlugin):
    """Example browser plugin that uses Camoufox browser,
    but otherwise keeps the functionality of PlaywrightBrowserPlugin.
    """

    @override
    async def new_browser(self) -> PlaywrightBrowserController:
        if not self._playwright:
            raise RuntimeError('Playwright browser plugin is not initialized.')

        # NOTE: Overwrite browser options
        self._browser_launch_options.update({"headless": False})

        return PlaywrightBrowserController(
            browser = await AsyncNewBrowser(
                self._playwright,
                **self._browser_launch_options
            ),
            # Increase, if camoufox can handle it in your use case.
            max_open_pages_per_browser=1,
            # This turns off the crawlee header_generation. Camoufox has its own.
            header_generator=None,
        )


