import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = ROOT_DIR / "src"

for p in (ROOT_DIR, SRC_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from flask import Flask

from config import settings
from logger import setup_logging

from src.web.api.api import api_main_bp


setup_logging()


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
