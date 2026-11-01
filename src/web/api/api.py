from flask import Blueprint

from .v1 import api_v1_bp
from config import settings

from constants import Web

api_main_bp = Blueprint("API", __name__)


api_main_bp.register_blueprint(api_v1_bp, url_prefix=Web.API_V1_STR)
