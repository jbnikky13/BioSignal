"""Leakage-aware evaluation utilities for independently labelled AMR signals.

This module deliberately does not generate reference labels. Callers must provide
an independently adjudicated or prospectively defined outcome and preserve its
provenance. Threshold selection must occur on development data only.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from itertools import product
from math import sqrt
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True)
class Thresholds:
    alert_rate: float
    alert_change: float
    minimum_samples: int = 20

    def __post_init__(self) -> None:
        if not 0 <= self.alert_rate <= 1:
            raise ValueError("alert_rate must be between 0 and 1")
        if not 0 <= self.alert_change <= 1:
            raise ValueError("alert_change must be between 0 and 1")
        if self.minimum_samples < 1:
            raise ValueError("minimum_samples must be at least 1")


@dataclass(frozen=True)
class BinaryMetrics:
    n: int
    positives: int
    negatives: int
    true_positive: int
    false_positive: int
    true_negative: int
    false_negative: int
    sensitivity: float | None
    specificity: float | None
    positive_predictive_value: float | None
    negative_predictive_value: float | None
    false_positive_rate: float | None
    sensitivity_wilson_95: tuple[float, float] | None
    specificity_wilson_95: tuple[float, float] | None
    ppv_wilson_95: tuple[float, float] | None


def wilson_interval(successes: int, trials: int, *, z: float = 1.959963984540054) -> tuple[float, float]:
    """Wilson interval for a binomial proportion; returns unit-interval bounds."""
    if trials <= 0:
        raise ValueError("trials must be greater than zero")
    if not 0 <= successes <= trials:
        raise ValueError("successes must be between zero and trials")
    if z <= 0:
        raise ValueError("z must be greater than zero")
    p = successes / trials
    z2 = z * z
    denominator = 1 + z2 / trials
    center = (p + z2 / (2 * trials)) / denominator
    half = z * sqrt(p * (1 - p) / trials + z2 / (4 * trials * trials)) / denominator
    return max(0.0, center - half), min(1.0, center + half)


def _parse_day(value: object, field: str) -> date:
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an ISO date (YYYY-MM-DD)") from exc


def validate_rows(rows: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    """Validate externally labelled records without creating or imputing labels.

    Required fields: period_end, current_rate, previous_rate, sample_count,
    previous_sample_count, reference_outcome, reference_source, protocol_id,
    and surveillance_unit. Rates are proportions in [0, 1]. A missing previous
    rate is allowed and disables the change-based rule for that record.
    """
    required = {
        "period_end", "current_rate", "sample_count",
        "reference_outcome", "reference_source", "protocol_id",
        "surveillance_unit",
    }
    result: list[dict[str, object]] = []
    for index, row in enumerate(rows, start=1):
        missing = sorted(key for key in required if key not in row or row[key] is None or row[key] == "")
        if missing:
            raise ValueError(f"row {index} missing required fields: {', '.join(missing)}")
        normalized = dict(row)
        normalized["period_end"] = _parse_day(row["period_end"], "period_end")
        normalized.setdefault("previous_rate", None)
        for field in ("current_rate", "previous_rate"):
            value = row[field]
            if value is None or value == "":
                if field == "previous_rate":
                    normalized[field] = None
                    continue
                raise ValueError(f"row {index} {field} is required")
            try:
                numeric = float(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"row {index} {field} must be numeric") from exc
            if not 0 <= numeric <= 1:
                raise ValueError(f"row {index} {field} must be between 0 and 1")
            normalized[field] = numeric
        normalized.setdefault("previous_sample_count", None)
        for field in ("sample_count", "previous_sample_count"):
            value = row[field]
            if value is None or value == "":
                if field == "previous_sample_count":
                    normalized[field] = None
                    continue
                raise ValueError(f"row {index} {field} is required")
            try:
                count = int(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"row {index} {field} must be an integer") from exc
            if count < 0 or (field == "sample_count" and count == 0):
                raise ValueError(f"row {index} {field} has an invalid count")
            normalized[field] = count
        outcome = row["reference_outcome"]
        if outcome not in (0, 1, False, True, "0", "1"):
            raise ValueError(f"row {index} reference_outcome must be independently labelled 0 or 1")
        normalized["reference_outcome"] = int(outcome)
        if not str(row["reference_source"]).strip() or not str(row["protocol_id"]).strip():
            raise ValueError(f"row {index} must record reference_source and protocol_id")
        if not str(row["surveillance_unit"]).strip():
            raise ValueError(f"row {index} surveillance_unit must be non-empty")
        result.append(normalized)
    if not result:
        raise ValueError("at least one labelled row is required")
    return result


def predict_alert(row: Mapping[str, object], thresholds: Thresholds) -> bool:
    """Apply the current heuristic alert rule to one validated record."""
    current_rate = float(row["current_rate"])
    current_n = int(row["sample_count"])
    previous_rate = row.get("previous_rate")
    previous_n = row.get("previous_sample_count")
    if current_n < thresholds.minimum_samples:
        return False
    rate_trigger = current_rate >= thresholds.alert_rate
    change_trigger = (
        previous_rate is not None
        and previous_n is not None
        and int(previous_n) >= thresholds.minimum_samples
        and current_rate - float(previous_rate) >= thresholds.alert_change
    )
    return rate_trigger or change_trigger


def binary_metrics(labels: Sequence[int], predictions: Sequence[bool]) -> BinaryMetrics:
    if len(labels) != len(predictions) or not labels:
        raise ValueError("labels and predictions must have equal, non-zero length")
    if any(label not in (0, 1) for label in labels):
        raise ValueError("labels must be binary")
    tp = sum(label == 1 and bool(pred) for label, pred in zip(labels, predictions))
    fp = sum(label == 0 and bool(pred) for label, pred in zip(labels, predictions))
    tn = sum(label == 0 and not bool(pred) for label, pred in zip(labels, predictions))
    fn = sum(label == 1 and not bool(pred) for label, pred in zip(labels, predictions))
    positives, negatives = tp + fn, tn + fp

    def ratio(num: int, den: int) -> float | None:
        return num / den if den else None

    return BinaryMetrics(
        n=len(labels),
        positives=positives,
        negatives=negatives,
        true_positive=tp,
        false_positive=fp,
        true_negative=tn,
        false_negative=fn,
        sensitivity=ratio(tp, positives),
        specificity=ratio(tn, negatives),
        positive_predictive_value=ratio(tp, tp + fp),
        negative_predictive_value=ratio(tn, tn + fn),
        false_positive_rate=ratio(fp, negatives),
        sensitivity_wilson_95=wilson_interval(tp, positives) if positives else None,
        specificity_wilson_95=wilson_interval(tn, negatives) if negatives else None,
        ppv_wilson_95=wilson_interval(tp, tp + fp) if tp + fp else None,
    )


def chronological_split(
    rows: Sequence[Mapping[str, object]], *, holdout_start: date | str
) -> tuple[list[Mapping[str, object]], list[Mapping[str, object]]]:
    """Split strictly by period_end; the holdout date belongs only to test."""
    cutoff = _parse_day(holdout_start, "holdout_start")
    train = [row for row in rows if _parse_day(row["period_end"], "period_end") < cutoff]
    test = [row for row in rows if _parse_day(row["period_end"], "period_end") >= cutoff]
    if not train or not test:
        raise ValueError("chronological split requires non-empty development and holdout periods")
    return train, test


def select_thresholds(
    development_rows: Sequence[Mapping[str, object]],
    *,
    alert_rates: Sequence[float],
    alert_changes: Sequence[float],
    minimum_samples: int = 20,
) -> tuple[Thresholds, BinaryMetrics]:
    """Choose thresholds on development data by Youden's J only.

    This objective must be pre-registered before looking at holdout results.
    Ties are broken toward higher thresholds (more conservative alerts).
    """
    if not development_rows:
        raise ValueError("development data cannot be empty")
    labels = [int(row["reference_outcome"]) for row in development_rows]
    candidates: list[tuple[float, float, Thresholds, BinaryMetrics]] = []
    for rate, change in product(alert_rates, alert_changes):
        thresholds = Thresholds(float(rate), float(change), minimum_samples)
        metrics = binary_metrics(labels, [predict_alert(row, thresholds) for row in development_rows])
        if metrics.sensitivity is None or metrics.specificity is None:
            continue
        j = metrics.sensitivity + metrics.specificity - 1
        candidates.append((j, thresholds.alert_rate + thresholds.alert_change, thresholds, metrics))
    if not candidates:
        raise ValueError("development data must contain both positive and negative reference outcomes")
    _, _, selected, metrics = max(candidates, key=lambda item: (item[0], item[1], item[2].alert_rate, item[2].alert_change))
    return selected, metrics


def evaluate_holdout(
    holdout_rows: Sequence[Mapping[str, object]], thresholds: Thresholds
) -> BinaryMetrics:
    """Evaluate frozen thresholds once on untouched holdout records."""
    if not holdout_rows:
        raise ValueError("holdout data cannot be empty")
    labels = [int(row["reference_outcome"]) for row in holdout_rows]
    predictions = [predict_alert(row, thresholds) for row in holdout_rows]
    return binary_metrics(labels, predictions)



def roc_auc(labels: Sequence[int], scores: Sequence[float]) -> float:
    """Compute rank-based AUROC for a heuristic score against independent labels.

    This assesses discrimination only. It does not calibrate the score as a
    probability. Tied scores receive average ranks.
    """
    if len(labels) != len(scores) or not labels:
        raise ValueError("labels and scores must have equal, non-zero length")
    if any(label not in (0, 1) for label in labels):
        raise ValueError("labels must be binary")
    positives = sum(labels)
    negatives = len(labels) - positives
    if positives == 0 or negatives == 0:
        raise ValueError("AUROC requires both positive and negative reference labels")
    if any(not 0 <= float(score) <= 1 for score in scores):
        raise ValueError("scores must be between 0 and 1")

    order = sorted(range(len(scores)), key=lambda index: float(scores[index]))
    rank_sum_positive = 0.0
    cursor = 0
    while cursor < len(order):
        end = cursor + 1
        score = float(scores[order[cursor]])
        while end < len(order) and float(scores[order[end]]) == score:
            end += 1
        average_rank = ((cursor + 1) + end) / 2
        rank_sum_positive += average_rank * sum(labels[order[i]] for i in range(cursor, end))
        cursor = end
    return (rank_sum_positive - positives * (positives + 1) / 2) / (positives * negatives)
