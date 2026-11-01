
from browser.driver import ChessDriver


async def run_driver():
    driver = ChessDriver()

    await driver.lunch_bot(
        "https://www.chess.com/play/computer"        
    )

    