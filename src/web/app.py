import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from flask import Flask

from config import settings
from src.web.api.api import api_main_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(settings.model_dump())

    app.register_blueprint(api_main_bp)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        debug=True, port=5000
    )
