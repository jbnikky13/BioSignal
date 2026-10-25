from datetime import date

import pytest

from biosignal.models import AMRObservation
from biosignal.signals import detect_amr_signal


def observation(
    resistant: int,
    tested: int = 100,
    *,
    period_start: date = date(2026, 1, 1),
    period_end: date = date(2026, 3, 31),
) -> AMRObservation:
    return AMRObservation(
        organism="Escherichia coli",
        antimicrobial="ciprofloxacin",
        period_start=period_start,
        period_end=period_end,
        tested_count=tested,
        resistant_count=resistant,
        region="example-region",
        source="synthetic",
    )


def test_detects_rising_resistance_and_reports_both_sample_sizes():
    previous = observation(20, tested=100, period_start=date(2025, 10, 1), period_end=date(2025, 12, 31))
    current = observation(35, tested=100)

    signal = detect_amr_signal(current, previous)

    assert signal.severity == "watch"
    assert signal.change == 0.15
    assert signal.previous_sample_count == 100
    assert "increased" in signal.explanation
    assert "n=100" in signal.explanation
    assert signal.quality_notes == ()


def test_marks_small_samples_as_insufficient_and_warns_about_instability():
    signal = detect_amr_signal(observation(10, tested=10))

    assert signal.severity == "insufficient_data"
    assert "unstable" in signal.explanation


def test_baseline_signal():
    signal = detect_amr_signal(observation(5))

    assert signal.severity == "baseline"
    assert signal.current_rate == 0.05
    assert "not a validated epidemiological threshold" in signal.explanation


def test_overlapping_periods_are_explicitly_flagged():
    previous = observation(
        20,
        period_start=date(2026, 1, 1),
        period_end=date(2026, 3, 31),
    )
    current = observation(
        35,
        period_start=date(2026, 3, 1),
        period_end=date(2026, 5, 31),
    )

    signal = detect_amr_signal(current, previous)

    assert signal.severity == "watch"
    assert len(signal.quality_notes) == 1
    assert "overlap" in signal.quality_notes[0]
    assert "overlap" in signal.explanation


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"minimum_samples": 0}, "minimum_samples"),
        ({"alert_rate": -0.1}, "alert_rate"),
        ({"alert_rate": 1.1}, "alert_rate"),
        ({"alert_change": -0.1}, "alert_change"),
        ({"alert_change": 1.1}, "alert_change"),
    ],
)
def test_rejects_invalid_signal_thresholds(kwargs, message):
    with pytest.raises(ValueError, match=message):
        detect_amr_signal(observation(5), **kwargs)
