from pathlib import Path
from typing import Final

ENCODING: Final[str] = "utf-8"
MAX_NEW_TOKENS: Final[int] = 1024

DATA_PATH: Final[Path] = Path(__file__).parent.parent / "data"
