import asyncio

from flask import Blueprint, jsonify

from browser.helpers import run_driver


bp = Blueprint("App", __name__)


@bp.route("/start", methods=["GET"])
def start_bot():
    asyncio.run(run_driver())
    
    return jsonify(
        {"status": "success", "message": "Bot started"}
    )
