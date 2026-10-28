#!/usr/bin/env python3
"""Audit a downloaded WHO GLASS dashboard resistance CSV without fitting thresholds."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from biosignal.who_glass import parse_who_glass_export, summarize_country_years


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate and summarize the country-level rows in a WHO GLASS resistance CSV export."
    )
    parser.add_argument("csv_path", type=Path, help="WHO GLASS dashboard CSV downloaded via the chart's data export")
    parser.add_argument(
        "--normalized-csv",
        type=Path,
        help="optional destination for normalized country-year observations",
    )
    args = parser.parse_args()

    text = args.csv_path.read_text(encoding="utf-8-sig")
    metadata, rows = parse_who_glass_export(text)
    result = {
        "source_file": args.csv_path.name,
        "dashboard_filters": metadata,
        "summary": summarize_country_years(rows),
        "validation_status": "passed_structural_checks_not_scientific_validation",
        "limitations": [
            "Dashboard export may omit source release/version and detailed laboratory comparability metadata.",
            "Pooled rates are descriptive and are not global population estimates.",
            "Structural integrity checks do not demonstrate representativeness or forecast performance.",
            "This script does not invent independent outcome labels or tune alert thresholds.",
        ],
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if args.normalized_csv:
        args.normalized_csv.parent.mkdir(parents=True, exist_ok=True)
        fields = list(rows[0].keys())
        with args.normalized_csv.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
