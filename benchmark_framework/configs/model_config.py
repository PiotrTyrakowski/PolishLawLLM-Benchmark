from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelConfig:
    """
    A dataclass to hold configuration settings for a model.
    """

    google_search: bool = False
    quantize: Optional[str] = None
    batch_size: Optional[int] = None
    chunk_size: int = 64
