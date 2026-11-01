from flask import Blueprint

from .routes import (
    bot
)


api_v1_bp = Blueprint("v1", __name__)


api_v1_bp.register_blueprint(bot.bp, url_prefix="/bot")
