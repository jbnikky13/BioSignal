from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class AMRObservation:
    """An aggregated antimicrobial susceptibility observation.

    Counts must represent an aggregated dataset, not an individual patient.
    """

    organism: str
    antimicrobial: str
    period_start: date
    period_end: date
    tested_count: int
    resistant_count: int
    region: Optional[str] = None
    source: Optional[str] = None

    def __post_init__(self) -> None:
        if self.tested_count <= 0:
            raise ValueError("tested_count must be greater than zero")
        if not 0 <= self.resistant_count <= self.tested_count:
            raise ValueError("resistant_count must be between 0 and tested_count")
        if self.period_end < self.period_start:
            raise ValueError("period_end cannot precede period_start")

    @property
    def resistance_rate(self) -> float:
        return self.resistant_count / self.tested_count
