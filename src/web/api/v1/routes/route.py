import asyncio

from flask import Blueprint

from browser.helpers import run_driver


bp = Blueprint("App", __name__)


@bp.route("/run_bot", methods=["GET"])
def run_bot():
    asyncio.run(
        run_driver()
    )

    return "Run bot"
    