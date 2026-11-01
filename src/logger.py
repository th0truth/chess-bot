import logging

from constants import LOGGER_FORMAT


_configured = False


def setup_logging(level: int = logging.INFO):
    global _configured

    if _configured:
        return

    logging.basicConfig(level=level, format=LOGGER_FORMAT)
    _configured = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
