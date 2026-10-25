from datetime import date

import pytest

from biosignal.models import AMRObservation
from biosignal.quality import QualityAssessment, assess_quality


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

    assert assessment.data_quality_score < 0.8
    assert "region unavailable" in assessment.reasons
    assert "source metadata unavailable" in assessment.reasons


def test_complete_large_period_has_high_heuristic_score_but_is_not_calibrated():
    assessment = assess_quality(observation())

    assert assessment.data_quality_score == 1.0
    assert assessment.data_quality_label == "higher_data_quality_score"
    assert assessment.calibration_status == "uncalibrated_heuristic"


def test_quality_flags_small_sample_and_short_window():
    assessment = assess_quality(
        observation(tested_count=5, start=date(2026, 1, 1), end=date(2026, 1, 7))
    )

    assert "very small sample" in assessment.reasons
    assert "short observation window" in assessment.reasons
    assert assessment.temporal_score < 1.0


def test_legacy_confidence_aliases_warn_and_remain_compatible():
    assessment = QualityAssessment(
        sample_score=1.0,
        completeness_score=1.0,
        temporal_score=1.0,
        data_quality_score=0.9,
        data_quality_label="higher_data_quality_score",
        reasons=(),
    )

    with pytest.warns(DeprecationWarning, match="not statistical confidence"):
        assert assessment.confidence_score == 0.9
    with pytest.warns(DeprecationWarning, match="data_quality_label"):
        assert assessment.label == "higher_data_quality_score"


@pytest.mark.parametrize("target_samples", [0, -1])
def test_quality_rejects_nonpositive_sample_target(target_samples: int):
    with pytest.raises(ValueError, match="target_samples must be greater than zero"):
        assess_quality(observation(), target_samples=target_samples)
