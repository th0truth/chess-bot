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
        raw_pieces = await cls._extract_raw_pieces(
            page 
        )

        return raw_pieces

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