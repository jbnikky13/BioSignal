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
    previous_sample_count: Optional[int] = None
    quality_notes: tuple[str, ...] = ()


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
    epidemiological threshold. Period overlap is surfaced as a caveat rather
    than silently treated as independent sequential evidence.
    """
    if minimum_samples < 1:
        raise ValueError("minimum_samples must be at least 1")
    if not 0 <= alert_rate <= 1:
        raise ValueError("alert_rate must be between 0 and 1")
    if not 0 <= alert_change <= 1:
        raise ValueError("alert_change must be between 0 and 1")

    previous_rate = previous.resistance_rate if previous else None
    previous_sample_count = previous.tested_count if previous else None
    raw_change = (
        current.resistance_rate - previous_rate
        if previous_rate is not None
        else None
    )
    change = round(raw_change, 12) if raw_change is not None else None

    quality_notes: list[str] = []
    if previous is not None and current.period_start <= previous.period_end:
        quality_notes.append(
            "Current and previous observation periods overlap; interpret the "
            "change cautiously because the periods may not be independent."
        )

    if current.tested_count < minimum_samples:
        severity = "insufficient_data"
        explanation = (
            f"Only {current.tested_count} observations are available; "
            f"the configured minimum is {minimum_samples}. The rate is "
            "unstable at this sample size and should not be interpreted alone."
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
            previous_sample_count,
            tuple(quality_notes),
        )

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
            f"{current.tested_count} tested observations. This is a research "
            "watch heuristic, not a validated epidemiological threshold."
        )
    else:
        direction = "increased" if change >= 0 else "decreased"
        explanation = (
            f"Resistance for {current.organism} against {current.antimicrobial} "
            f"{direction} by {abs(change):.1%} versus the previous period "
            f"({previous_rate:.1%}, n={previous_sample_count}, to "
            f"{current.resistance_rate:.1%}, n={current.tested_count}). "
            "Interpret the comparison in light of sample sizes and surveillance "
            "coverage; this is not a causal conclusion."
        )
        if quality_notes:
            explanation += " " + " ".join(quality_notes)

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
        previous_sample_count,
        tuple(quality_notes),
    )
