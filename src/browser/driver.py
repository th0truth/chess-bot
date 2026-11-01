from typing import Optional, Literal
from collections.abc import AsyncGenerator

from patchright.async_api import (
    Playwright, BrowserContext,
    Page, Locator, async_playwright
) 

from logger import get_logger

from browser.parser import BoardParser

from engine import StockfishEngine


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

    async def run(self, url: str):
        await self._ensure_connected()

        page = (
            self._context.pages[0]
            if self._context.pages
            else await self._context.new_page()
        )

        try:
            await page.goto(url, wait_until="domcontentloaded")
        except Exception as e:
            logger.warning(
                f"[-] Failed to load {url}: {e}"
            )

        board_selector = "wc-chess-board"

        await page.wait_for_selector(f"{board_selector} .piece")

        board_elem = page.locator(board_selector)

        async with StockfishEngine() as engine:
            async for fen in self._parse_board(page, board_elem):
                analysis = await engine.get_best_move(fen)

                logger.info(analysis)

    async def _parse_board(
        self, page: Page, board_elem: Locator
    ) -> AsyncGenerator[str, None, None]:
        parser = BoardParser()

        classes = await board_elem.get_attribute("class") or ""

        my_color = "BLACK" if "flipped" in classes else "WHITE"

        logger.info(
            f"[MATCH JOINED] Playing as: {my_color}"
        )

        last_fen = None

        while True:
            active_turn = await self._determine_turn(page, board_elem)
            current_fen = await parser.extract_fen(page, active_turn)

            if current_fen != last_fen:
                last_fen = current_fen
                yield current_fen
            
            await page.wait_for_timeout(5000)

    async def _determine_turn(
        self, page: Page, board_elem: Locator
    ) -> Literal["w", "b"]:
        has_highlights = await board_elem.locator(f".highlight").count() > 0

        if not has_highlights:
            active_turn = "w"
        else:
            move_nodes = await page.locator(
                "vertical-move-list .node"
            ).count()
            active_turn = "w" if (move_nodes % 2 == 0) else "b"

        return active_turn
