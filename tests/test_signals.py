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
    region: str | None = "example-region",
    source: str | None = "synthetic",
    specimen_type: str | None = "urine",
    testing_criteria: str | None = "EUCAST 2025",
    laboratory_method: str | None = "disk diffusion",
) -> AMRObservation:
    return AMRObservation(
        organism="Escherichia coli",
        antimicrobial="ciprofloxacin",
        period_start=period_start,
        period_end=period_end,
        tested_count=tested,
        resistant_count=resistant,
        region=region,
        source=source,
        specimen_type=specimen_type,
        testing_criteria=testing_criteria,
        laboratory_method=laboratory_method,
    )


def test_detects_rising_resistance_and_reports_both_sample_sizes():
    previous = observation(20, tested=100, period_start=date(2025, 10, 1), period_end=date(2025, 12, 31))
    current = observation(35, tested=100)

    signal = detect_amr_signal(current, previous)

    assert signal.severity == "watch"
    assert signal.change == 0.15
    assert signal.previous_sample_count == 100
    assert "increased" in signal.explanation
    assert "15.0 percentage points" in signal.explanation
    assert "n=100" in signal.explanation
    assert signal.quality_notes == ()
    assert signal.comparison_status == "no_known_mismatch"
    assert signal.current_rate_interval_95 is not None
    assert signal.current_rate_interval_95 is not None
    assert signal.previous_rate_interval_95 is not None
    assert signal.current_rate_interval_95[0] < signal.current_rate < signal.current_rate_interval_95[1]
    assert "not been calibrated against surveillance outcomes" in signal.explanation
    assert "Wilson 95% interval" in signal.explanation


def test_marks_small_samples_as_insufficient_and_warns_about_instability():
    signal = detect_amr_signal(observation(10, tested=10))

    assert signal.severity == "insufficient_data"
    assert "unstable" in signal.explanation


def test_baseline_signal():
    signal = detect_amr_signal(observation(5))

    assert signal.severity == "baseline"
    assert signal.current_rate == 0.05
    assert signal.comparison_status == "not_assessed"
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
    assert signal.comparison_status == "caution"


def test_source_change_is_flagged_as_possible_surveillance_coverage_shift():
    previous = observation(20, period_start=date(2025, 10, 1), period_end=date(2025, 12, 31), source="lab-A")
    current = observation(35, source="lab-B")

    signal = detect_amr_signal(current, previous)

    assert signal.severity == "watch"
    assert any("Source changed" in note for note in signal.quality_notes)
    assert "surveillance coverage" in signal.explanation
    assert signal.comparison_status == "caution"


def test_region_change_is_flagged_when_comparing_observations_directly():
    previous = observation(20, period_start=date(2025, 10, 1), period_end=date(2025, 12, 31), region="north")
    current = observation(35, region="south")

    signal = detect_amr_signal(current, previous)

    assert any("Region changed" in note for note in signal.quality_notes)
    assert "geographic coverage" in signal.explanation
    assert signal.comparison_status == "caution"


def test_missing_coverage_metadata_is_explicitly_flagged():
    signal = detect_amr_signal(observation(25, region=None, source=None))

    assert any("missing region or source" in note for note in signal.quality_notes)
    assert "cannot be fully assessed" in signal.explanation
    assert signal.comparison_status == "not_assessed"


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



def test_missing_comparability_metadata_is_flagged():
    signal = detect_amr_signal(
        observation(25, specimen_type=None, testing_criteria=None, laboratory_method=None)
    )

    assert any("specimen type" in note for note in signal.quality_notes)
    assert any("testing criteria" in note for note in signal.quality_notes)
    assert any("laboratory method" in note for note in signal.quality_notes)
    assert signal.comparison_status == "not_assessed"


def test_changed_comparability_metadata_is_flagged():
    previous = observation(
        20,
        period_start=date(2025, 10, 1),
        period_end=date(2025, 12, 31),
        specimen_type="blood",
        testing_criteria="CLSI 2024",
        laboratory_method="broth microdilution",
    )
    current = observation(35)

    signal = detect_amr_signal(current, previous)

    assert any("specimen type" in note for note in signal.quality_notes)
    assert any("testing criteria" in note for note in signal.quality_notes)
    assert any("laboratory method" in note for note in signal.quality_notes)
    assert signal.comparison_status == "caution"



def test_case_and_whitespace_only_metadata_differences_are_not_mismatches():
    previous = observation(
        20,
        period_start=date(2025, 10, 1),
        period_end=date(2025, 12, 31),
        region=" North ",
        source=" Public Lab ",
        specimen_type="Urine",
        testing_criteria="EUCAST 2025",
        laboratory_method="Disk Diffusion",
    )
    current = observation(
        35,
        region="north",
        source="public lab",
        specimen_type=" urine ",
        testing_criteria="eucast 2025",
        laboratory_method="disk diffusion",
    )

    signal = detect_amr_signal(current, previous)

    assert signal.region == "north"
    assert signal.quality_notes == ()
    assert signal.comparison_status == "no_known_mismatch"


def test_small_previous_sample_does_not_trigger_trend_watch():
    previous = observation(
        0,
        tested=5,
        period_start=date(2025, 10, 1),
        period_end=date(2025, 12, 31),
    )
    current = observation(15, tested=100)

    signal = detect_amr_signal(current, previous, minimum_samples=20)

    assert signal.change == 0.15
    assert signal.severity == "baseline"
    assert signal.previous_sample_count == 5
    assert any("below the configured minimum" in note for note in signal.quality_notes)
    assert "not used to trigger a watch alert" in signal.explanation


def test_alert_change_is_absolute_percentage_points():
    previous = observation(
        20,
        period_start=date(2025, 10, 1),
        period_end=date(2025, 12, 31),
    )
    current = observation(30)

    signal = detect_amr_signal(current, previous, alert_rate=0.50, alert_change=0.10)

    assert signal.change == 0.10
    assert signal.severity == "watch"
    assert "10.0 percentage points" in signal.explanation



def test_wilson_interval_handles_zero_and_all_successes():
    from biosignal.signals import wilson_interval

    zero = wilson_interval(0, 20)
    all_successes = wilson_interval(20, 20)

    assert zero[0] == 0.0
    assert 0.0 < zero[1] < 0.5
    assert all_successes[1] == 1.0
    assert 0.5 < all_successes[0] < 1.0


@pytest.mark.parametrize(
    ("successes", "trials"),
    [(-1, 10), (11, 10), (0, 0)],
)
def test_wilson_interval_rejects_invalid_counts(successes, trials):
    from biosignal.signals import wilson_interval

    with pytest.raises(ValueError):
        wilson_interval(successes, trials)
