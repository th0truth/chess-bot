from typing import Optional, Annotated

from patchright.async_api import TimeoutError as PWTimeout
from patchright.async_api import (
    Playwright, BrowserContext,
    Page, Locator,
    async_playwright
) 

from logger import get_logger



logger = get_logger(__name__)


class ChessDriver:
    def __init__(self):
        self._pw: Optional[Playwright] = None
        self._context: Optional[BrowserContext] = None

    async def connect(self):
        """Establish connection to ChessDriver"""

        try:
            context_kwargs = {
                "channel": "chromium",
                "headless": True,
                "viewport": {
                    "width": 1366, "height": 768
                },
                "timezone_id": "Europe/Kyiv",
                "locale": "uk-UA",
                "args": [
                    "--disable-blink-features=AutomationControlled"
                ]
            }

            self._pw = await async_playwright().start()
            self._context = await self._pw.chromium.launch_persistent_context(
                **context_kwargs
            )

            self._context.on(
                "close", lambda _: setattr(self, "_context", None)
            )
        except Exception as e:
            logger.error(
                f"Failed to initialize ChessDriver connection: {e}",
                exc_info=True
            )
            
            await self.close()

            raise


    async def close(self):
        """Close connection to ChessDriver"""

        if self._context:
            try:
                await self._context.close()
            except Exception as e:
                logger.debug(
                    f"Context close failed (already dead?): {e}"
                )
            
            self._context = None

        if self._pw:
            try:
                await self._pw.stop()
            except Exception as e:
                logger.debug(
                    f"Playwright stop failed (already dead?): {e}"
                )
                
            self._pw = None

    async def _ensure_connected(self):
        """Ensure reconnection ChessDriver"""

        if self._context and self._pw:
            return

        logger.warning(
            "ChessDriver disconnected - reconnecting..."
        )

        await self.close()
        await self.connect()