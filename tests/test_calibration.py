from datetime import date

import pytest

from biosignal.calibration import (
    Thresholds,
    binary_metrics,
    chronological_split,
    evaluate_holdout,
    external_unit_split,
    predict_alert,
    roc_auc,
    select_thresholds,
    validate_rows,
)


def row(day, outcome, current, previous, *, n=100, previous_n=100, unit="site-A"):
    return {
        "period_end": day,
        "current_rate": current,
        "previous_rate": previous,
        "sample_count": n,
        "previous_sample_count": previous_n,
        "reference_outcome": outcome,
        "reference_source": "independent adjudication protocol v1",
        "protocol_id": "AMR-OUTCOME-2026-v1",
        "surveillance_unit": unit,
    }


def test_validation_requires_independent_label_provenance():
    record = row("2025-01-01", 1, 0.4, 0.2)
    record.pop("reference_source")
    with pytest.raises(ValueError, match="reference_source"):
        validate_rows([record])


def test_validation_rejects_rate_outside_unit_interval():
    with pytest.raises(ValueError, match="current_rate must be between 0 and 1"):
        validate_rows([row("2025-01-01", 1, 1.2, 0.2)])


def test_prediction_obeys_minimum_sample_safeguard():
    record = row("2025-01-01", 1, 0.5, 0.1, n=10)
    assert not predict_alert(record, Thresholds(0.2, 0.1, minimum_samples=20))


def test_chronological_split_does_not_mix_future_into_development():
    records = [
        row("2024-12-31", 0, 0.05, 0.04),
        row("2025-01-01", 1, 0.4, 0.1),
    ]
    train, test = chronological_split(records, holdout_start="2025-01-01")
    assert len(train) == 1
    assert len(test) == 1
    assert train[0]["period_end"] == "2024-12-31"


def test_threshold_selection_uses_development_and_holdout_is_separate():
    train = [
        row("2023-01-01", 0, 0.05, 0.04),
        row("2023-02-01", 0, 0.08, 0.05),
        row("2023-03-01", 1, 0.50, 0.10),
        row("2023-04-01", 1, 0.45, 0.15),
    ]
    thresholds, development_metrics = select_thresholds(
        train,
        alert_rates=[0.2, 0.3, 0.4],
        alert_changes=[0.1, 0.2, 0.3],
    )
    assert development_metrics.n == 4
    # Holdout data are evaluated after thresholds have been selected.
    test = [
        row("2024-01-01", 1, 0.60, 0.10),
        row("2024-02-01", 0, 0.05, 0.04),
    ]
    metrics = evaluate_holdout(test, thresholds)
    assert metrics.n == 2
    assert metrics.sensitivity is not None
    assert metrics.specificity is not None


def test_metrics_include_uncertainty_intervals_and_denominators():
    metrics = binary_metrics([1, 1, 0, 0], [True, False, True, False])
    assert metrics.n == 4
    assert metrics.true_positive == 1
    assert metrics.false_positive == 1
    assert metrics.true_negative == 1
    assert metrics.false_negative == 1
    assert metrics.sensitivity_wilson_95 is not None
    assert metrics.specificity_wilson_95 is not None
    assert metrics.ppv_wilson_95 is not None


def test_empty_or_single_class_training_data_is_not_silently_scored():
    with pytest.raises(ValueError, match="non-empty"):
        chronological_split([], holdout_start=date(2025, 1, 1))
    with pytest.raises(ValueError, match="both positive and negative"):
        select_thresholds(
            [row("2023-01-01", 1, 0.5, 0.1)],
            alert_rates=[0.2],
            alert_changes=[0.1],
        )



def test_quality_score_auc_measures_discrimination_not_probability_calibration():
    assert roc_auc([0, 0, 1, 1], [0.1, 0.3, 0.7, 0.9]) == 1.0
    assert roc_auc([0, 1], [0.5, 0.5]) == 0.5


def test_quality_score_auc_requires_both_reference_classes():
    with pytest.raises(ValueError, match="both positive and negative"):
        roc_auc([1, 1], [0.2, 0.8])



def test_external_unit_split_keeps_surveillance_units_disjoint():
    records = [
        row("2023-01-01", 0, 0.05, 0.04, unit="site-A"),
        row("2023-02-01", 1, 0.45, 0.10, unit="site-B"),
        row("2023-03-01", 0, 0.08, 0.05, unit="site-C"),
    ]
    train, test = external_unit_split(records, holdout_units={"site-B"})
    assert {r["surveillance_unit"] for r in train} == {"site-A", "site-C"}
    assert {r["surveillance_unit"] for r in test} == {"site-B"}


def test_external_unit_split_rejects_missing_partition():
    records = [row("2023-01-01", 0, 0.05, 0.04, unit="site-A")]
    with pytest.raises(ValueError, match="non-empty development and holdout"):
        external_unit_split(records, holdout_units={"site-A"})
