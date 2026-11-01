from flask import Blueprint


bp = Blueprint("App", __name__)


@bp.route("/run_bot", methods=["GET"])
def run_bot():
    return "hello, world"
    