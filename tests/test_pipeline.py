from datetime import date

from biosignal.models import AMRObservation
from biosignal.pipeline import run


def obs(period_start: date, resistant: int) -> AMRObservation:
    return AMRObservation(
        organism="Escherichia coli",
        antimicrobial="ciprofloxacin",
        period_start=period_start,
        period_end=period_start,
        tested_count=100,
        resistant_count=resistant,
        region="example",
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
