"""Small orchestration layer for producing AMR signals."""

from collections.abc import Iterable

from .models import AMRObservation
from .signals import AMRSignal, detect_amr_signal


def compare_periods(
    current: AMRObservation,
    previous: AMRObservation | None = None,
) -> AMRSignal:
    """Generate one explainable signal from two aggregated periods."""
    return detect_amr_signal(current, previous)


def run(
    observations: Iterable[AMRObservation],
) -> list[AMRSignal]:
    """Pair chronological observations within each organism/drug/region.

    Inputs are sorted internally so callers cannot accidentally compare
    periods in arrival order. Ties are stable; duplicate or overlapping
    periods remain visible to the caller and are not silently discarded.
    """
    ordered = sorted(
        observations,
        key=lambda item: (
            item.organism.strip().casefold(),
            item.antimicrobial.strip().casefold(),
            item.region.strip().casefold() if item.region and item.region.strip() else "",
            item.period_start,
            item.period_end,
        ),
    )
    signals: list[AMRSignal] = []
    previous: AMRObservation | None = None
    previous_key: tuple[str, str, str | None] | None = None

    for current in ordered:
        # Group using normalized labels so case/outer whitespace differences do
        # not split one organism/drug/region series. Keep original labels on output.
        key = (
            current.organism.strip().casefold(),
            current.antimicrobial.strip().casefold(),
            current.region.strip().casefold() if current.region and current.region.strip() else None,
        )
        if key != previous_key:
            previous = None

        signals.append(compare_periods(current, previous))
        previous = current
        previous_key = key

    return signals
