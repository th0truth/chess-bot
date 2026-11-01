from flask import Blueprint

from .v1 import api_v1_bp
from config import settings


api_main_bp = Blueprint("API", __name__)


api_main_bp.register_blueprint(api_v1_bp, url_prefix=settings.API_V1_STR)
