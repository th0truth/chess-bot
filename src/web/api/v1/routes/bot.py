import asyncio

from flask import Blueprint, jsonify

from browser.helpers import run_driver

from constants import Chess


bp = Blueprint("App", __name__)


@bp.route("/play/<mode>", methods=["GET"])
def start(mode):
    match mode:
        case "computer":
            url = Chess.COMPUTER
        case "online":
            url = Chess.ONLINE
        
    asyncio.run(run_driver(url))
    
    return jsonify(
        {"status": "success", "message": "Bot started"}
    )
