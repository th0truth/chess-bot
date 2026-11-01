from pathlib import Path
import asyncio
import sys


ROOT_DIR = Path(__file__).resolve().parent.parent
print(ROOT_DIR)
SRC_DIR = ROOT_DIR / "src"

for p in (ROOT_DIR, SRC_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


from src.browser.helpers import run_driver


if __name__ == "__main__":
    asyncio.run(run_driver())
