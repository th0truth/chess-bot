from dataclasses import dataclass


LOGGER_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


@dataclass
class Chess:
    MAIN_URL        = "https://www.chess.com"
    COMPUTER        = f"{MAIN_URL}/play/computer"
    ONLINE          = f"{MAIN_URL}/play/online"
    COMPETITIVE     = f"{MAIN_URL}/game"


@dataclass
class Web:
    API_V1_STR = "/api/v1"
