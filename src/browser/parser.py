from typing import List, Dict

from patchright.async_api import Page


class BoardParser:
    PIECE_MAP = {
        "wp": "P", "wn": "N", "wb": "B", "wr": "R", "wq": "Q", "wk": "K",
        "bp": "p", "bn": "n", "bb": "b", "br": "r", "bq": "q", "bk": "k"
    }

    @classmethod
    async def extract_fen(
        cls, page: Page, active_turn: str
    ):
        raw_pieces = await cls._extract_raw_pieces(page)

        board = [
            ["" for _ in range(8)]
            for _ in range(8)
        ]

        for item in raw_pieces:
            piece_code = item["piece"]
            square = item["square"]

            col = int(square[0]) - 1
            row = 8 - int(square[1])

            fen_char = cls.PIECE_MAP.get(piece_code)

            if fen_char:
                board[row][col] = fen_char

        fen_rows = []

        for row in board:
            empty = 0
            row_str = ""

            for cell in row:
                if cell == "":
                    empty += 1
                else:
                    if empty > 0:
                        row_str += str(empty)
                        empty = 0

                    row_str += cell

            if empty > 0:
                row_str += str(empty)

            fen_rows.append(row_str)        

        fen = f"{'/'.join(fen_rows)} {active_turn} KQkq - 0 1"

        return fen

    @staticmethod
    async def _extract_raw_pieces(page: Page) -> List[Dict[str, str]]:
        js_code = """
            () => {
                const pieces = [];
                const pieceElements = document.querySelectorAll(
                    'wc-chess-board .piece'
                );
                
                pieceElements.forEach(el => {
                        const classes = Array.from(el.classList);                
                        const pieceClass = classes.find(
                            c => /^[wb][pnbrqk]$/.test(c)
                        );
                        const squareClass = classes.find(
                            c => /^square-\\d{2}$/.test(c)
                        );

                        if (pieceClass && squareClass) {
                            const squareCoord = squareClass.replace(
                                'square-', ''
                            );
                            pieces.push(
                                { piece: pieceClass, square: squareCoord }
                            );
                        }
                });       

                return pieces;
            }
        """

        return await page.evaluate(js_code)
