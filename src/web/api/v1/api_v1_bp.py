from flask import Blueprint

from .routes import (
    route
)


api_v1_bp = Blueprint("v1", __name__)


api_v1_bp.register_blueprint(route.bp, url_prefix="/script")
