from typing import Optional, Dict, Any

import chess
import chess.engine

from config import settings
from logger import get_logger 


logger = get_logger(__name__)


class StockfishEngine:
    def __init__(
        self,
        path: Optional[str] = settings.STOCKFISH_ENGINE_PATH
    ):
        self._engine: Optional[chess.engine.UciProtocol] = None
        self._transport = None
        self.path = path

    async def __aenter__(self):
        if not self.path:
            raise ValueError(
                "STOCKFISH_ENGINE_PATH is not configured"
            )

        if not self._engine:
            self._transport, self._engine = await chess.engine.popen_uci(
                f"{self.path}"
            )

        logger.info("[+] Stockfish connected and ready!")

        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._engine:
            await self._engine.quit()
            self._engine = None

    async def get_best_move(
        self, fen: str, time_limit: float = 0.2, *, chess960: bool = False
    ) -> Optional[Dict[str, Any]]:
        board = chess.Board(fen, chess960=chess960)
        time_limit = chess.engine.Limit(time_limit)

        try:
            result = await self._engine.play(board, time_limit)
            best_move_uci = result.move.uci() if result.move else None

            return {
                "move": best_move_uci,
                "from_square": best_move_uci[:2] or None,
                "to_square": best_move_uci[2:4] or None
            }
        except (
            chess.engine.EngineTerminatedError, chess.engine.EngineError
        ) as e:
            logger.warning(
                f"Engine connection dropped: {e}, reconnecting..."
            )

            self._engine = None
            await self.__aenter__()
            
            return
