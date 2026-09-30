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
    """Pair sequential observations for each organism/drug/region.

    Input should already be sorted by organism, antimicrobial, region,
    and period_start.
    """
    signals: list[AMRSignal] = []
    previous: AMRObservation | None = None
    previous_key: tuple[str, str, str | None] | None = None

    for current in observations:
        key = (current.organism, current.antimicrobial, current.region)
        if key != previous_key:
            previous = None

        signals.append(compare_periods(current, previous))
        previous = current
        previous_key = key

    return signals
