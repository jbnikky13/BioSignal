from dataclasses import dataclass
from math import sqrt
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
    current_rate_interval_95: tuple[float, float] | None = None
    previous_rate_interval_95: tuple[float, float] | None = None


def wilson_interval(successes: int, trials: int, *, z: float = 1.959963984540054) -> tuple[float, float]:
    """Return a two-sided Wilson score interval for a binomial proportion.

    This quantifies binomial sampling uncertainty only. It does not correct for
    biased sampling, clustering, repeated isolates, case-mix shifts, or other
    surveillance-design limitations.
    """
    if trials <= 0:
        raise ValueError("trials must be greater than zero")
    if not 0 <= successes <= trials:
        raise ValueError("successes must be between zero and trials")
    if z <= 0:
        raise ValueError("z must be greater than zero")

    p = successes / trials
    z2 = z * z
    denominator = 1 + z2 / trials
    center = (p + z2 / (2 * trials)) / denominator
    half_width = (
        z
        * sqrt((p * (1 - p) / trials) + (z2 / (4 * trials * trials)))
        / denominator
    )
    return (max(0.0, center - half_width), min(1.0, center + half_width))


def _normalized(value: str | None) -> str | None:
    """Normalize comparison text without changing labels stored for display."""
    return value.strip().casefold() if value and value.strip() else None


def detect_amr_signal(
    current: AMRObservation,
    previous: Optional[AMRObservation] = None,
    *,
    minimum_samples: int = 20,
    alert_rate: float = 0.20,
    alert_change: float = 0.10,
) -> AMRSignal:
    """Create a transparent AMR research signal, not a validated alert.

    alert_change is an absolute resistance-rate difference expressed as a
    proportion: 0.10 means a 10-percentage-point increase, not a 10% relative
    increase. Thresholds are configurable heuristics, not validated
    epidemiological cutoffs. Wilson intervals quantify binomial sampling
    uncertainty only and do not establish representativeness or comparability.
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
    current_interval = wilson_interval(current.resistant_count, current.tested_count)
    previous_interval = (
        wilson_interval(previous.resistant_count, previous.tested_count)
        if previous is not None
        else None
    )

    quality_notes: list[str] = []
    if _normalized(current.region) is None or _normalized(current.source) is None:
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
        if _normalized(getattr(current, field)) is None
    ]
    if missing_current:
        quality_notes.append(
            "Current observation is missing comparability metadata: "
            + ", ".join(missing_current) + "."
        )

    if previous is not None:
        changed_fields = [
            label for field, label in comparability_fields
            if _normalized(getattr(current, field)) is not None
            and _normalized(getattr(previous, field)) is not None
            and _normalized(getattr(current, field)) != _normalized(getattr(previous, field))
        ]
        missing_previous = [
            label for field, label in comparability_fields
            if _normalized(getattr(previous, field)) is None
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
        if _normalized(current.region) != _normalized(previous.region):
            quality_notes.append(
                "Region changed between observations; the rate difference may "
                "reflect geographic coverage rather than a temporal trend."
            )
        if _normalized(current.source) != _normalized(previous.source):
            quality_notes.append(
                "Source changed between observations; differences in reporting "
                "or surveillance coverage may explain part of the rate change."
            )
        if _normalized(previous.region) is None or _normalized(previous.source) is None:
            quality_notes.append(
                "Previous observation has missing region or source metadata; "
                "surveillance coverage cannot be fully compared."
            )
        if previous.tested_count < minimum_samples:
            quality_notes.append(
                f"Previous observation has only {previous.tested_count} tested "
                f"observations, below the configured minimum of {minimum_samples}; "
                "the period-to-period change is not used to trigger a watch alert."
            )

    previous_sample_sufficient = (
        previous is None or previous.tested_count >= minimum_samples
    )
    if current.tested_count < minimum_samples:
        severity = "insufficient_data"
        explanation = (
            f"Only {current.tested_count} observations are available; "
            f"the configured minimum is {minimum_samples}. The rate is "
            "unstable at this sample size and should not be interpreted alone."
        )
    elif current.resistance_rate >= alert_rate or (
        change is not None
        and previous_sample_sufficient
        and change >= alert_change
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

    interval_text = (
        f" Current resistance rate Wilson 95% interval: "
        f"{current_interval[0]:.1%}–{current_interval[1]:.1%}."
    )
    if previous_interval is not None:
        interval_text += (
            f" Previous rate Wilson 95% interval: "
            f"{previous_interval[0]:.1%}–{previous_interval[1]:.1%}."
        )
    explanation += interval_text
    explanation += (
        " Alert thresholds are configurable research heuristics and have not been "
        "calibrated against surveillance outcomes. Wilson intervals quantify "
        "binomial sampling uncertainty only; they do not account for sampling "
        "bias, clustering, duplicate isolates, or representativeness."
    )
    if quality_notes:
        explanation += " " + " ".join(quality_notes)

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
        current_interval,
        previous_interval,
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
        f"{direction} by {abs(change) * 100:.1f} percentage points versus the previous period "
        f"({previous_rate:.1%}, n={previous_sample_count}, to "
        f"{current.resistance_rate:.1%}, n={current.tested_count}). "
        "Interpret the comparison in light of sample sizes and surveillance "
        "coverage; this is not a causal conclusion."
    )
