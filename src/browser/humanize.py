from typing import Optional, Tuple
import asyncio
import random

from patchright.async_api import Page, Locator

from logger import get_logger


logger = get_logger(__name__)


class Humanize:
    @classmethod
    async def make_moves(
        cls, page: Page, board_elem: Locator,
        from_square: str, to_square: str,
        is_flipped: bool, promotion: Optional[str] = None
    ):
        box = await board_elem.bounding_box()

        if not box:
            logger.error("Could not find chessboard bounding box.")

            return            

        from_x, from_y = cls._square_to_coords(from_square, box, is_flipped)
        to_x, to_y = cls._square_to_coords(to_square, box, is_flipped)

        # Click the piece to select it
        await page.mouse.click(from_x, from_y)

        await asyncio.sleep(random.random())

        # Click destination to place it
        await page.mouse.click(to_x, to_y)

        # Handle pawn promotion modal if applicable
        if promotion:
            await asyncio.sleep(0.15)

            promo_selector = (
                f".promotion-piece.{
                    'b' if is_flipped else 'w'
                }{promotion.lower()}"
            )

            if await board_elem.locator(promo_selector).is_visible():
                await page.locator(promo_selector).click()

    @staticmethod
    def _square_to_coords(square: str, box: dict, is_flipped: bool) -> Tuple:
        col = ord(square[0].lower()) - ord('a')
        rank = int(square[1])

        square_size = box["width"] / 8.0

        if is_flipped:
            x_idx = 7 - col
            y_idx = rank - 1
        else:
            x_idx = col
            y_idx = 8 - rank

        center_x = box["x"] + (x_idx + 0.5) * square_size
        center_y = box["y"] + (y_idx + 0.5) * square_size

        return center_x, center_y
 