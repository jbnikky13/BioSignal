#!/usr/bin/env python3
"""Build descriptive WHO GLASS geography/time summaries; no alert fitting."""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
from biosignal.who_glass import parse_who_glass_export, summarize_country_years, summarize_geography_time

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a WHO GLASS dashboard export and build descriptive country/WHO-region time summaries.")
    parser.add_argument("csv_path", type=Path, help="WHO GLASS dashboard CSV downloaded from the chart data export")
    parser.add_argument("--output-json", type=Path, required=True, help="destination for descriptive summary JSON")
    parser.add_argument("--country-year-csv", type=Path, help="optional normalized country-year CSV")
    parser.add_argument("--region-year-csv", type=Path, help="optional WHO-region/year summary CSV")
    args = parser.parse_args()
    metadata, rows = parse_who_glass_export(args.csv_path.read_text(encoding="utf-8-sig"))
    result = {
        "source_file": args.csv_path.name,
        "dashboard_filters": metadata,
        "country_year_summary": summarize_country_years(rows),
        "geography_time_summary": summarize_geography_time(rows),
        "status": "descriptive_structural_checks_only_not_scientific_validation",
        "limitations": [
            "WHO regions are broad reporting groupings, not subnational geography.",
            "Pooled rates weight countries by interpretable AST denominators and are not global or population-representative estimates.",
            "Country contributions, denominators, and year coverage must be reviewed before comparing regions or years.",
            "This tool does not infer missing countries, impute observations, generate independent outcomes, or fit alert thresholds.",
        ],
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.country_year_csv:
        args.country_year_csv.parent.mkdir(parents=True, exist_ok=True)
        with args.country_year_csv.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    if args.region_year_csv:
        summaries = result["geography_time_summary"]["region_year"]
        args.region_year_csv.parent.mkdir(parents=True, exist_ok=True)
        with args.region_year_csv.open("w", newline="", encoding="utf-8") as handle:
            fields = list(summaries[0]) if summaries else ["who_region", "year"]
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(summaries)
    print(json.dumps({"output_json": str(args.output_json), "country_year_rows": len(rows),
                      "region_year_rows": len(result["geography_time_summary"]["region_year"]),
                      "status": result["status"]}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
