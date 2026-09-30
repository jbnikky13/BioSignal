from datetime import date

from biosignal.models import AMRObservation
from biosignal.signals import detect_amr_signal


def observation(resistant: int, tested: int = 100) -> AMRObservation:
    return AMRObservation(
        organism="Escherichia coli",
        antimicrobial="ciprofloxacin",
        period_start=date(2026, 1, 1),
        period_end=date(2026, 3, 31),
        tested_count=tested,
        resistant_count=resistant,
        region="example-region",
        source="synthetic",
    )


def test_detects_rising_resistance():
    previous = observation(20)
    current = observation(35)

    signal = detect_amr_signal(current, previous)

    assert signal.severity == "watch"
    assert signal.change == 0.15
    assert "increased" in signal.explanation


def test_marks_small_samples_as_insufficient():
    signal = detect_amr_signal(observation(10, tested=10))

    assert signal.severity == "insufficient_data"


def test_baseline_signal():
    signal = detect_amr_signal(observation(5))

    assert signal.severity == "baseline"
    assert signal.current_rate == 0.05
