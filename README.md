# chess-bot

Stealth [Chess.com](https://www.chess.com/) asynchronous bot powered by [Stockfish Engine](https://stockfishchess.org/), Patchright (undetected Playwright), and a Flask RESTful API.

## Features

- **Stealth Automation**: Uses [`Patchright`](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright) with persistent Chrome profiles to bypass Cloudflare CAPTCHA and human-like movements to avoid detections.
- **Board Parsing**: Real-time DOM board scraping and FEN generation from active Chess.com matches.
- **Engine Analysis**: Stockfish integration via [`python-chess`](https://python-chess.readthedocs.io/en/latest/) for move evaluation.
- **Dual Control**: Run directly via CLI script or trigger through a local Flask RESTful API.

---

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- Google Chrome installed locally
- [Stockfish binary](https://stockfishchess.org/download/)

---

## Installation

```bash
git clone https://github.com/th0truth/chess-bot.git && cd chess-bot
```

### Configuration

```bash
cp .env.example .env

# Path to your Chrome user profile directory (to keep Chess.com login session)
CHESS_PROFILE_DIR=/path/to/chrome/user-data

# Path to the Stockfish executable
STOCKFISH_ENGINE_PATH=/usr/games/stockfish
```

---

## Quickstart


### Install dependencies

```bash
uv sync
uv run patchright install chrome

# or install chrome directly on machine
```

### Run the bot

```bash
uv run flask --app src.web.app run
curl http://localhost:5000/api/v1/bot/start

# or via CLI
python3 scripts/run_bot.py
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for complete details.

