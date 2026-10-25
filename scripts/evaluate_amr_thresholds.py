#!/usr/bin/env python3
"""Evaluate AMR alert thresholds against independently labelled CSV records."""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict
from pathlib import Path

from biosignal.calibration import (
    Thresholds,
    chronological_split,
    evaluate_holdout,
    external_unit_split,
    select_thresholds,
    validate_rows,
)


def _floats(value: str) -> list[float]:
    try:
        values = [float(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected comma-separated numeric values") from exc
    if not values or any(not 0 <= item <= 1 for item in values):
        raise argparse.ArgumentTypeError("values must be non-empty proportions between 0 and 1")
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path, help="CSV following data/examples/calibration_template.csv")
    split = parser.add_mutually_exclusive_group(required=True)
    split.add_argument("--holdout-start", help="ISO date; records on/after this date are held out")
    split.add_argument("--holdout-units", help="comma-separated surveillance_unit values reserved for holdout")
    parser.add_argument("--alert-rates", type=_floats, default=[0.1, 0.2, 0.3])
    parser.add_argument("--alert-changes", type=_floats, default=[0.05, 0.1, 0.15])
    parser.add_argument("--minimum-samples", type=int, default=20)
    parser.add_argument("--output", type=Path, help="optional JSON output path")
    args = parser.parse_args()

    with args.csv_path.open(newline="", encoding="utf-8-sig") as handle:
        records = validate_rows(csv.DictReader(handle))

    if args.holdout_start:
        development, holdout = chronological_split(records, holdout_start=args.holdout_start)
        split_description = {"type": "chronological", "holdout_start": args.holdout_start}
    else:
        units = {unit.strip() for unit in args.holdout_units.split(",") if unit.strip()}
        development, holdout = external_unit_split(records, holdout_units=units)
        split_description = {"type": "external_surveillance_unit", "holdout_units": sorted(units)}

    thresholds, development_metrics = select_thresholds(
        development,
        alert_rates=args.alert_rates,
        alert_changes=args.alert_changes,
        minimum_samples=args.minimum_samples,
    )
    holdout_metrics = evaluate_holdout(holdout, thresholds)
    report = {
        "status": "exploratory_evaluation_not_automatically_scientific_validation",
        "split": split_description,
        "record_counts": {"total": len(records), "development": len(development), "holdout": len(holdout)},
        "selected_thresholds": asdict(thresholds),
        "development_metrics": asdict(development_metrics),
        "holdout_metrics": asdict(holdout_metrics),
        "interpretation": (
            "Thresholds were selected on development records and evaluated on a held-out set. "
            "This does not establish scientific validity unless the dataset is representative, "
            "the reference outcome is independent and pre-specified, and coverage/label quality "
            "have been reviewed by domain experts."
        ),
    }
    rendered = json.dumps(report, indent=2, default=lambda value: list(value) if isinstance(value, tuple) else str(value))
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
