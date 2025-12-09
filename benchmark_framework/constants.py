from typing import Final, Dict
from pathlib import Path

ENCODING: Final[str] = "utf-8"
MAX_NEW_TOKENS: Final[int] = 1024

DATA_PATH: Final[Path] = Path(__file__).parent.parent / "data"
RESULTS_PATH: Final[Path] = Path(__file__).parent.parent / "results"
ROOT_PATH: Final[Path] = Path(__file__).parent.parent
