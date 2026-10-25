from datetime import date

import pytest

from biosignal.models import AMRObservation
from biosignal.quality import assess_quality


def observation(
    *,
    tested_count: int = 100,
    region: str | None = "Nigeria",
    source: str | None = "WHO GLASS-AMR",
    start: date = date(2026, 1, 1),
    end: date = date(2026, 3, 31),
) -> AMRObservation:
    return AMRObservation(
        organism="E. coli",
        antimicrobial="ciprofloxacin",
        period_start=start,
        period_end=end,
        tested_count=tested_count,
        resistant_count=min(20, tested_count),
        region=region,
        source=source,
    )


def test_quality_penalizes_missing_metadata():
    assessment = assess_quality(observation(region=None, source=None, tested_count=25))

    assert assessment.confidence_score < 0.8
    assert "region unavailable" in assessment.reasons
    assert "source metadata unavailable" in assessment.reasons


def test_complete_large_period_scores_higher_but_is_not_calibrated():
    assessment = assess_quality(observation())

    assert assessment.confidence_score == 1.0
    assert assessment.label == "higher_data_confidence"
    assert assessment.calibration_status == "uncalibrated_heuristic"


def test_quality_flags_small_sample_and_short_window():
    assessment = assess_quality(
        observation(tested_count=5, start=date(2026, 1, 1), end=date(2026, 1, 7))
    )

    assert "very small sample" in assessment.reasons
    assert "short observation window" in assessment.reasons
    assert assessment.temporal_score < 1.0


@pytest.mark.parametrize("target_samples", [0, -1])
def test_quality_rejects_nonpositive_sample_target(target_samples: int):
    with pytest.raises(ValueError, match="target_samples must be greater than zero"):
        assess_quality(observation(), target_samples=target_samples)
