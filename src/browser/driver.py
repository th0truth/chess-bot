from typing import Optional

from patchright.async_api import TimeoutError as PWTimeout
from patchright.async_api import (
    Playwright, BrowserContext, Page,
    async_playwright
) 

from logger import get_logger

from browser.parser import BoardParser


logger = get_logger(__name__)


class ChessDriver:
    def __init__(
        self,
        profile_dir: Optional[str] = None
    ):
        self._pw: Optional[Playwright] = None
        self._context: Optional[BrowserContext] = None
        self.profile_dir = profile_dir

    async def connect(self):
        """Establish connection to ChessDriver"""

        if not self.profile_dir:
            logger.warning(
                f"ChessDriver without profile session"
            )

        try:
            context_kwargs = {
                "channel": "chrome",
                "headless": False,
                "viewport": {
                    "width": 1366, "height": 768
                },
                "timezone_id": "Europe/Kyiv",
                "locale": "uk-UA",
            }

            self._pw = await async_playwright().start()
            self._context = await self._pw.chromium.launch_persistent_context(
                user_data_dir=self.profile_dir,
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
                    f"Context close failed: {e}"
                )
            
            self._context = None

        if self._pw:
            try:
                await self._pw.stop()
            except Exception as e:
                logger.debug(
                    f"[-] Playwright close failed: {e}"
                )
                
            self._pw = None

    async def _ensure_connected(self):
        """Ensure reconnection ChessDriver"""

        if self._context and self._pw:
            return

        logger.warning(
            "[-] ChessDriver disconnected - reconnecting..."
        )

        await self.close()
        await self.connect()

    async def run(
        self, url: str, attempts: int = 2
    ):
        await self._ensure_connected()

        page = (
            self._context.pages[0]
            if self._context.pages
            else await self._context.new_page()
        )

        for attempt in range(attempts):
            try:
                logger.info(
                    f"Navigating to {url} (attempt {attempt + 1}/{attempts})..."
                )

                await page.goto(url, wait_until="domcontentloaded")

                break
            except Exception as e:
                logger.warning(
                    f"Goto failed (attempt {attempt + 1}/{attempts}): {e}"
                )
                
                await page.wait_for_timeout(3000)

        await self.parse_board(page)

    async def parse_board(self, page: Page) -> str:
        parser = BoardParser()
        board_selector = "wc-chess-board"

        await page.wait_for_selector(f"{board_selector} .piece")

        classes = await page.locator(
            board_selector
        ).get_attribute("class") or ""

        my_color = "b" if "flipped" in classes else "w"

        has_highlights = await page.locator(
            f"{board_selector} .highlight"
        ).count() > 0

        if not has_highlights:
            active_turn = "w"
        else:
            move_nodes = await page.locator(
                "vertical-move-list .node"
            ).count()
            active_turn = "w" if (move_nodes % 2 == 0) else "b"

        fen = await parser.extract_fen(page, active_turn)

        logger.info(f"[FEN]: {fen}")
        logger.info(f"My color: {my_color}")

        return fen
        