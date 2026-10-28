"""Pre-specified country-held-out evaluation for independently labelled AMR outcomes."""
from __future__ import annotations
from dataclasses import asdict
from typing import Any, Mapping, Sequence
from biosignal.calibration import binary_metrics, external_unit_split, predict_alert, Thresholds, validate_rows

def validate_protocol(protocol: Mapping[str, Any]) -> dict[str, Any]:
    required = ("protocol_id", "outcome_definition", "expert_approval", "protocol_frozen_before_holdout_review", "holdout_countries", "thresholds", "baseline_thresholds")
    missing = [key for key in required if key not in protocol]
    if missing:
        raise ValueError(f"protocol missing required fields: {', '.join(missing)}")
    approval = protocol["expert_approval"]
    if not isinstance(approval, dict) or approval.get("status") != "approved":
        raise ValueError("expert_approval.status must be 'approved' before evaluation")
    for field in ("expert_role", "approval_date", "approval_reference"):
        if not str(approval.get(field, "")).strip():
            raise ValueError(f"expert_approval.{field} is required")
    if protocol["protocol_frozen_before_holdout_review"] is not True:
        raise ValueError("protocol must be frozen before holdout outcomes are reviewed")
    if not str(protocol["outcome_definition"]).strip():
        raise ValueError("outcome_definition must be explicit")
    holdout = protocol["holdout_countries"]
    if not isinstance(holdout, list) or not holdout or any(not str(c).strip() for c in holdout):
        raise ValueError("holdout_countries must be a non-empty list")
    if len({str(c) for c in holdout}) != len(holdout):
        raise ValueError("holdout_countries contains duplicates")
    for key in ("thresholds", "baseline_thresholds"):
        if not isinstance(protocol[key], dict):
            raise ValueError(f"{key} must be an object")
    for key in ("alert_rate", "alert_change_percentage_points", "minimum_samples"):
        if key not in protocol["thresholds"]:
            raise ValueError(f"thresholds.{key} is required")
    for key in ("current_rate", "change_percentage_points"):
        if key not in protocol["baseline_thresholds"]:
            raise ValueError(f"baseline_thresholds.{key} is required")
    t = protocol["thresholds"]
    Thresholds(float(t["alert_rate"]), float(t["alert_change_percentage_points"]) / 100, int(t["minimum_samples"]))
    b = protocol["baseline_thresholds"]
    if not 0 <= float(b["current_rate"]) <= 1:
        raise ValueError("baseline_thresholds.current_rate must be between 0 and 1")
    if not 0 <= float(b["change_percentage_points"]) <= 100:
        raise ValueError("baseline_thresholds.change_percentage_points must be between 0 and 100")
    return dict(protocol)

def _predictions(rows: Sequence[Mapping[str, Any]], protocol: Mapping[str, Any]) -> dict[str, list[bool]]:
    t, b = protocol["thresholds"], protocol["baseline_thresholds"]
    min_n = int(t["minimum_samples"])
    combined = Thresholds(float(t["alert_rate"]), float(t["alert_change_percentage_points"]) / 100, min_n)
    result = {name: [] for name in ("always_negative", "current_rate_baseline", "change_only_baseline", "biosignal_combined_rule")}
    for row in rows:
        enough = int(row["sample_count"]) >= min_n
        previous, previous_n = row.get("previous_rate"), row.get("previous_sample_count")
        enough_previous = previous is not None and previous_n is not None and int(previous_n) >= min_n
        result["always_negative"].append(False)
        result["current_rate_baseline"].append(enough and float(row["current_rate"]) >= float(b["current_rate"]))
        result["change_only_baseline"].append(enough and enough_previous and float(row["current_rate"]) - float(previous) >= float(b["change_percentage_points"]) / 100)
        result["biosignal_combined_rule"].append(predict_alert(row, combined))
    return result

def evaluate_country_holdout(records: Sequence[Mapping[str, Any]], protocol_input: Mapping[str, Any]) -> dict[str, Any]:
    protocol = validate_protocol(protocol_input)
    rows = validate_rows(records)
    if {str(r["protocol_id"]) for r in rows} != {str(protocol["protocol_id"])}:
        raise ValueError("every labelled row protocol_id must match the frozen evaluation protocol_id")
    holdout_units = {str(unit) for unit in protocol["holdout_countries"]}
    units = {str(r["surveillance_unit"]) for r in rows}
    if holdout_units - units:
        raise ValueError(f"holdout countries absent from dataset: {sorted(holdout_units - units)}")
    development, holdout = external_unit_split(rows, holdout_units=holdout_units)
    labels = [int(r["reference_outcome"]) for r in holdout]
    predictions = _predictions(holdout, protocol)
    metrics = {name: asdict(binary_metrics(labels, pred)) for name, pred in predictions.items()}
    country_breakdown = {}
    for country in sorted(holdout_units):
        country_rows = [r for r in holdout if str(r["surveillance_unit"]) == country]
        ys = [int(r["reference_outcome"]) for r in country_rows]
        country_predictions = _predictions(country_rows, protocol)
        country_breakdown[country] = {"records": len(country_rows), "positive_outcomes": sum(ys), "rules": {
            name: {"alerts": sum(pred), "true_positives": sum(y == 1 and p for y, p in zip(ys, pred)),
                   "false_positives": sum(y == 0 and p for y, p in zip(ys, pred)),
                   "true_negatives": sum(y == 0 and not p for y, p in zip(ys, pred)),
                   "false_negatives": sum(y == 1 and not p for y, p in zip(ys, pred))}
            for name, pred in country_predictions.items()}}
    return {
        "status": "exploratory_country_held_out_evaluation", "protocol_id": protocol["protocol_id"],
        "outcome_definition": protocol["outcome_definition"],
        "development_countries": sorted({str(r["surveillance_unit"]) for r in development}),
        "development_records": len(development), "holdout_countries": sorted(holdout_units),
        "holdout_records": len(holdout), "holdout_positive_outcomes": sum(labels),
        "metrics_by_rule": metrics, "holdout_country_breakdown": country_breakdown,
        "limitations": [
            "Outcome and thresholds must be frozen before examining holdout outcomes.",
            "Country holdout prevents country overlap, but repeated rows within a country may remain correlated.",
            "Row-level Wilson intervals do not account for country clustering; this script does not estimate cluster-aware uncertainty.",
            "This is not clinical validation; the outcome and protocol require AMR expert approval.",
            "data_quality_score remains an uncalibrated heuristic and requires separate independent expert-quality labels."
        ]}
