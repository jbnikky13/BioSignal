from datetime import date

from biosignal.models import AMRObservation
from biosignal.pipeline import run


def obs(
    period_start: date,
    resistant: int,
    *,
    organism: str = "Escherichia coli",
    antimicrobial: str = "ciprofloxacin",
    region: str | None = "example",
) -> AMRObservation:
    return AMRObservation(
        organism=organism,
        antimicrobial=antimicrobial,
        period_start=period_start,
        period_end=period_start,
        tested_count=100,
        resistant_count=resistant,
        region=region,
        source="synthetic",
    )


def test_pipeline_compares_sequential_periods():
    signals = run([
        obs(date(2026, 1, 1), 20),
        obs(date(2026, 4, 1), 35),
    ])

    assert signals[0].previous_rate is None
    assert signals[1].previous_rate == 0.20
    assert signals[1].change == 0.15


def test_pipeline_sorts_unsorted_periods_chronologically():
    signals = run([
        obs(date(2026, 4, 1), 35),
        obs(date(2026, 1, 1), 20),
    ])

    assert [signal.current_rate for signal in signals] == [0.20, 0.35]
    assert signals[0].previous_rate is None
    assert signals[1].previous_rate == 0.20
    assert signals[1].change == 0.15


def test_pipeline_does_not_compare_across_regions_or_organisms():
    signals = run([
        obs(date(2026, 1, 1), 20, region="north"),
        obs(date(2026, 4, 1), 35, region="south"),
        obs(date(2026, 4, 1), 40, organism="Klebsiella pneumoniae", region="north"),
    ])

    assert all(signal.previous_rate is None for signal in signals)
