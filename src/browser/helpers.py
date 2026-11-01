from browser.driver import ChessDriver

from constants import Chess

from browser.humanize import Humanize

from config import settings


async def run_driver(
    url: str = Chess.ONLINE
):
    driver = ChessDriver(settings.CHESS_PROFILE_DIR)

    await driver.run(url)
