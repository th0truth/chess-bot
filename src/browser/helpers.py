from browser.driver import ChessDriver

from constants import Chess


async def run_driver():
    driver = ChessDriver()

    await driver.run(Chess.COMPUTER)
