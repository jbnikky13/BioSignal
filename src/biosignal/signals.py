from dataclasses import dataclass
from typing import Optional

from .models import AMRObservation


@dataclass(frozen=True)
class AMRSignal:
    organism: str
    antimicrobial: str
    current_rate: float
    previous_rate: Optional[float]
    change: Optional[float]
    sample_count: int
    region: Optional[str]
    severity: str
    explanation: str


def detect_amr_signal(
    current: AMRObservation,
    previous: Optional[AMRObservation] = None,
    *,
    minimum_samples: int = 20,
    alert_rate: float = 0.20,
    alert_change: float = 0.10,
) -> AMRSignal:
    """Create a transparent AMR signal from aggregated observations.

    This is a research heuristic, not a clinical recommendation or
    epidemiological threshold.
    """
    if current.tested_count < minimum_samples:
        severity = "insufficient_data"
        explanation = (
            f"Only {current.tested_count} observations are available; "
            f"the configured minimum is {minimum_samples}."
        )
        return AMRSignal(
            current.organism,
            current.antimicrobial,
            current.resistance_rate,
            previous.resistance_rate if previous else None,
            (
                current.resistance_rate - previous.resistance_rate
                if previous else None
            ),
            current.tested_count,
            current.region,
            severity,
            explanation,
        )

    previous_rate = previous.resistance_rate if previous else None
    change = current.resistance_rate - previous_rate if previous_rate is not None else None

    if current.resistance_rate >= alert_rate or (
        change is not None and change >= alert_change
    ):
        severity = "watch"
    else:
        severity = "baseline"

    if previous_rate is None:
        explanation = (
            f"{current.organism} shows a {current.resistance_rate:.1%} "
            f"resistance rate to {current.antimicrobial} across "
            f"{current.tested_count} observations."
        )
    else:
        direction = "increased" if change >= 0 else "decreased"
        explanation = (
            f"Resistance for {current.organism} against {current.antimicrobial} "
            f"{direction} by {abs(change):.1%} versus the previous period "
            f"({previous_rate:.1%} to {current.resistance_rate:.1%})."
        )

    return AMRSignal(
        current.organism,
        current.antimicrobial,
        current.resistance_rate,
        previous_rate,
        change,
        current.tested_count,
        current.region,
        severity,
        explanation,
    )
