from browser.driver import ChessDriver

from constants import Chess

from config import settings


async def run_driver():
    driver = ChessDriver(settings.CHESS_PROFILE_DIR)

    await driver.run(Chess.COMPUTER)
