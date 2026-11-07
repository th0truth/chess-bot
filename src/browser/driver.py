from typing import Optional, Literal
from collections.abc import AsyncGenerator
import sys

from patchright.async_api import (
    Playwright, BrowserContext, Error,
    Page, Locator, async_playwright
)

from logger import get_logger

from constants import Chess 

from browser.parser import BoardParser
from browser.humanize import Humanize

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

        if not self._context:
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

        match url:
            case Chess.ONLINE:
                await Humanize.click_start_game(page)

                await page.wait_for_url(
                    f"{Chess.COMPETITIVE}/**", timeout=60000
                )

                await self._activate_bot(page)
            case Chess.COMPUTER:
                await self._activate_bot(page)
            case _:
                logger.warning(
                    f"Unsupported game mode: {url}"
                )

    async def _activate_bot(self, page: Page):
        board_selector = "wc-chess-board"

        while True:
            if page.is_closed():
                logger.info("Browser page closed.")

                break

            try:
                await page.wait_for_selector(f"{board_selector} .piece")
                board_elem = page.locator(board_selector)

                classes = await board_elem.get_attribute("class") or ""
                
                is_flipped = "flipped" in classes
                my_color = "BLACK" if is_flipped else "WHITE"
                my_side = "b" if is_flipped else "w"

                logger.info(
                    f"[MATCH JOINED] Playing as: {my_color}"
                )

                async with StockfishEngine() as engine:
                    async for fen in self._parse_board(page):
                        if not fen:
                            break

                        active_turn = fen.split()[1]

                        if active_turn == my_side: 
                            analysis = await engine.get_best_move(fen)

                            if analysis and analysis["move"]:
                                promotion_piece = (
                                    analysis["move"][4]
                                    if len(analysis["move"]) > 4 else None 
                                )

                                await Humanize.make_moves(
                                    page, board_elem,
                                    analysis["from_square"],
                                    analysis["to_square"],
                                    is_flipped, promotion_piece
                                )

                await page.locator(
                    ".game-over-modal-shell-container,"
                    ".game-over-dialog-component,"
                    ".board-dialog-component"
                ).wait_for(state="hidden")

                await page.wait_for_timeout(5000)
            except Error:
                logger.info("Browser was closed.")

                break

    async def _parse_board(
        self, page: Page
    ) -> AsyncGenerator[str, None, None]:
        parser = BoardParser() 

        last_fen = None

        while True:
            if await self._is_game_finished(page):
                logger.info("[MATCH FINISHED] Game over.")

                return
            
            active_turn = await self._determine_turn(page)
            current_fen = await parser.extract_fen(page, active_turn)
            
            if current_fen != last_fen:
                last_fen = current_fen

                yield current_fen
            
            await page.wait_for_timeout(300)

    async def _determine_turn(
        self, page: Page
    ) -> Literal["w", "b"]:
           return await page.evaluate(
                """
                () => {
                        const moveNodes = document.querySelectorAll(
                            'vertical-move-list .node, .move-list-component .node, wc-move-list .node, [data-ply]'
                        );
                        if (moveNodes.length > 0) {
                            return moveNodes.length % 2 === 0 ? 'w' : 'b';
                        }

                        const highlightEls = document.querySelectorAll('wc-chess-board .highlight');
                        if (!highlightEls || highlightEls.length < 2) {
                            return 'w';
                        }

                        const highlightSquares = [];
                        highlightEls.forEach(el => {
                            const sqClass = Array.from(el.classList).find(c => /^square-\\d{2}$/.test(c));
                            if (sqClass) highlightSquares.push(sqClass.replace('square-', ''));
                        });

                        const pieces = document.querySelectorAll('wc-chess-board .piece');
                        for (const piece of pieces) {
                            const classes = Array.from(piece.classList);
                            const sqClass = classes.find(c => /^square-\\d{2}$/.test(c));
                            if (!sqClass) continue;
                            const sq = sqClass.replace('square-', '');

                                    if (highlightSquares.includes(sq)) {
                                        const pieceType = classes.find(c => /^[wb][pnbrqk]$/.test(c));
                                        if (pieceType) {
                                            // If White just moved, next turn is Black ('b')
                                            // If Black just moved, next turn is White ('w')
                                            return pieceType[0] === 'w' ? 'b' : 'w';
                            }
                            }
                                }

                        return 'w';
                    }
    		    """
            )


    async def _is_game_finished(self, page: Page) -> bool:
        return await page.locator(
            ".game-over-modal-shell-container,"
            ".game-over-dialog-component,"
            ".board-dialog-component"
        ).is_visible()
