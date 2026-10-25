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
    comparison_status: str = "not_assessed"


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
    epidemiological threshold. Period overlap and observable source/region
    changes are surfaced as caveats; they are not statistically corrected.
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
    if not current.region or not current.source:
        quality_notes.append(
            "Current observation has missing region or source metadata; "
            "surveillance coverage cannot be fully assessed."
        )

    comparability_fields = (
        ("specimen_type", "specimen type"),
        ("testing_criteria", "testing criteria"),
        ("laboratory_method", "laboratory method"),
    )
    missing_current = [
        label for field, label in comparability_fields
        if not getattr(current, field)
    ]
    if missing_current:
        quality_notes.append(
            "Current observation is missing comparability metadata: "
            + ", ".join(missing_current) + "."
        )

    if previous is not None:
        changed_fields = [
            label for field, label in comparability_fields
            if getattr(current, field) and getattr(previous, field)
            and getattr(current, field) != getattr(previous, field)
        ]
        missing_previous = [
            label for field, label in comparability_fields
            if not getattr(previous, field)
        ]
        if changed_fields:
            quality_notes.append(
                "Comparability metadata changed for: "
                + ", ".join(changed_fields) + "."
            )
        if missing_previous:
            quality_notes.append(
                "Previous observation is missing comparability metadata: "
                + ", ".join(missing_previous) + "."
            )
        if current.period_start <= previous.period_end:
            quality_notes.append(
                "Current and previous observation periods overlap; interpret "
                "the change cautiously because the periods may not be independent."
            )
        if current.region != previous.region:
            quality_notes.append(
                "Region changed between observations; the rate difference may "
                "reflect geographic coverage rather than a temporal trend."
            )
        if current.source != previous.source:
            quality_notes.append(
                "Source changed between observations; differences in reporting "
                "or surveillance coverage may explain part of the rate change."
            )
        if not previous.region or not previous.source:
            quality_notes.append(
                "Previous observation has missing region or source metadata; "
                "surveillance coverage cannot be fully compared."
            )

    if current.tested_count < minimum_samples:
        severity = "insufficient_data"
        explanation = (
            f"Only {current.tested_count} observations are available; "
            f"the configured minimum is {minimum_samples}. The rate is "
            "unstable at this sample size and should not be interpreted alone."
        )
    elif current.resistance_rate >= alert_rate or (
        change is not None and change >= alert_change
    ):
        severity = "watch"
        explanation = _trend_explanation(
            current, previous, previous_rate, previous_sample_count, change
        )
    else:
        severity = "baseline"
        explanation = _trend_explanation(
            current, previous, previous_rate, previous_sample_count, change
        )

    if quality_notes:
        explanation += " " + " ".join(quality_notes)

    # This reports only checks supported by the current schema; it is not
    # proof that two surveillance datasets are fully comparable.
    comparison_status = (
        "not_assessed"
        if previous is None
        else "caution"
        if quality_notes
        else "no_known_mismatch"
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
        comparison_status,
    )


def _trend_explanation(
    current: AMRObservation,
    previous: Optional[AMRObservation],
    previous_rate: Optional[float],
    previous_sample_count: Optional[int],
    change: Optional[float],
) -> str:
    if previous is None or previous_rate is None or change is None:
        return (
            f"{current.organism} shows a {current.resistance_rate:.1%} "
            f"resistance rate to {current.antimicrobial} across "
            f"{current.tested_count} tested observations. This is a research "
            "watch heuristic, not a validated epidemiological threshold."
        )

    direction = "increased" if change >= 0 else "decreased"
    return (
        f"Resistance for {current.organism} against {current.antimicrobial} "
        f"{direction} by {abs(change):.1%} versus the previous period "
        f"({previous_rate:.1%}, n={previous_sample_count}, to "
        f"{current.resistance_rate:.1%}, n={current.tested_count}). "
        "Interpret the comparison in light of sample sizes and surveillance "
        "coverage; this is not a causal conclusion."
    )
