from dataclasses import dataclass
from typing import Optional


@dataclass
class RunnerConfig:
    """
    A dataclass to hold configuration settings for a benchmark runner.
    """

    requests_per_minute: Optional[int] = None
    daily_limit: Optional[int] = None
