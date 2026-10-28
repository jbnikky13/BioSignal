"""Importer and integrity checks for WHO GLASS dashboard resistance exports.

The dashboard CSV has filter/summary sections followed by a country-level table.
This module reads only the country-level table and never treats the chart's
Min/Q1/Median/Q3/Max summary as country observations or reference labels.
"""
from __future__ import annotations

import csv
import io
from collections import defaultdict
from typing import Any

SECTION_MARKER = "Data for line plots for individual CTAs"
REQUIRED_COLUMNS = (
    "Iso3",
    "CountryTerritoryArea",
    "WHORegionName",
    "Year",
    "Specimen",
    "PathogenName",
    "AbTargets",
    "TotalSpecimenIsolates",
    "InterpretableAST",
    "Resistant",
    "PercentResistant",
)
INTEGER_COLUMNS = ("Year", "TotalSpecimenIsolates", "InterpretableAST", "Resistant")
NUMERIC_COLUMNS = (*INTEGER_COLUMNS, "PercentResistant")


def parse_who_glass_export(text: str) -> tuple[dict[str, str], list[dict[str, Any]]]:
    """Return dashboard filter metadata and validated country-year observations."""
    lines = text.splitlines()
    try:
        marker_index = next(i for i, line in enumerate(lines) if line.strip() == SECTION_MARKER)
    except StopIteration as exc:
        raise ValueError(
            f"missing '{SECTION_MARKER}' section; download the chart's underlying data, not its image"
        ) from exc

    metadata: dict[str, str] = {}
    for line in lines[:marker_index]:
        stripped = line.strip().strip('"')
        if ":" in stripped and "filter" in stripped.lower():
            key, value = stripped.split(":", 1)
            metadata[key.strip()] = value.strip().strip('"')

    table_lines = lines[marker_index + 1 :]
    while table_lines and not table_lines[0].strip():
        table_lines.pop(0)
    reader = csv.DictReader(io.StringIO("\n".join(table_lines)))
    if not reader.fieldnames:
        raise ValueError("country-level table is missing its header")
    missing = sorted(set(REQUIRED_COLUMNS) - set(reader.fieldnames))
    if missing:
        raise ValueError(f"WHO GLASS country-level table is missing columns: {', '.join(missing)}")

    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, int]] = set()
    for line_number, raw in enumerate(reader, start=marker_index + 3):
        if not raw or not any((value or "").strip() for value in raw.values()):
            continue
        row: dict[str, Any] = {key: (raw.get(key) or "").strip() for key in REQUIRED_COLUMNS}
        for field in ("Iso3", "CountryTerritoryArea", "WHORegionName", "Specimen", "PathogenName", "AbTargets"):
            if not row[field]:
                raise ValueError(f"line {line_number}: {field} is blank")
        try:
            for field in INTEGER_COLUMNS:
                row[field] = int(row[field])
            row["PercentResistant"] = float(row["PercentResistant"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"line {line_number}: invalid numeric field") from exc

        if row["Year"] < 1900 or row["Year"] > 2200:
            raise ValueError(f"line {line_number}: implausible year {row['Year']}")
        for field in ("TotalSpecimenIsolates", "InterpretableAST", "Resistant"):
            if row[field] < 0:
                raise ValueError(f"line {line_number}: {field} cannot be negative")
        if row["InterpretableAST"] <= 0:
            raise ValueError(f"line {line_number}: InterpretableAST must be positive")
        if row["Resistant"] > row["InterpretableAST"]:
            raise ValueError(f"line {line_number}: Resistant exceeds InterpretableAST")
        if row["InterpretableAST"] > row["TotalSpecimenIsolates"]:
            raise ValueError(f"line {line_number}: InterpretableAST exceeds TotalSpecimenIsolates")
        if not 0 <= row["PercentResistant"] <= 100:
            raise ValueError(f"line {line_number}: PercentResistant must be between 0 and 100")
        calculated = 100 * row["Resistant"] / row["InterpretableAST"]
        if abs(calculated - row["PercentResistant"]) > 0.011:
            raise ValueError(
                f"line {line_number}: PercentResistant does not match Resistant / InterpretableAST"
            )

        key = (row["Iso3"], row["Year"])
        if key in seen:
            raise ValueError(f"duplicate country-year record: {key[0]} {key[1]}")
        seen.add(key)
        rows.append(row)

    if not rows:
        raise ValueError("WHO GLASS export contains no country-level observations")

    # Filters should agree with the data rows when specific values were selected.
    for filter_name, column in (
        ("Infection type filter", "Specimen"),
        ("Bacterial pathogen filter", "PathogenName"),
        ("Antibiotic filter", "AbTargets"),
    ):
        value = metadata.get(filter_name)
        if value and value.lower() not in {"all", "all available"}:
            observed = {str(row[column]).lower() for row in rows}
            expected = value.lower()
            # The dashboard uses "Bloodstream" as the label for the BLOOD specimen.
            if filter_name == "Infection type filter" and expected == "bloodstream":
                continue
            if observed != {expected}:
                raise ValueError(
                    f"{filter_name} says {value!r}, but country-level rows contain {sorted(observed)!r}"
                )

    return metadata, rows


def summarize_country_years(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Produce descriptive summaries; pooled rates are not global estimates."""
    if not rows:
        raise ValueError("rows cannot be empty")
    by_year: dict[int, dict[str, int]] = defaultdict(lambda: {"resistant": 0, "interpretable_ast": 0})
    by_country: dict[str, dict[int, float]] = defaultdict(dict)
    for row in rows:
        year = int(row["Year"])
        by_year[year]["resistant"] += int(row["Resistant"])
        by_year[year]["interpretable_ast"] += int(row["InterpretableAST"])
        by_country[str(row["Iso3"])][year] = float(row["PercentResistant"])

    yearly = []
    for year in sorted(by_year):
        counts = by_year[year]
        yearly.append({
            "year": year,
            "resistant": counts["resistant"],
            "interpretable_ast": counts["interpretable_ast"],
            "pooled_resistance_percent": round(100 * counts["resistant"] / counts["interpretable_ast"], 4),
        })

    years = sorted({int(row["Year"]) for row in rows})
    first_year, last_year = years[0], years[-1]
    endpoint_changes = [
        values[last_year] - values[first_year]
        for values in by_country.values()
        if first_year in values and last_year in values
    ]
    return {
        "country_year_rows": len(rows),
        "countries": len(by_country),
        "years": years,
        "duplicate_country_years": 0,
        "missing_required_values": 0,
        "balanced_country_panel": all(
            len(values) == len(years) and set(values) == set(years)
            for values in by_country.values()
        ),
        "yearly_pooled_descriptive_rates": yearly,
        "countries_with_increase_from_first_to_last_year": sum(change > 0 for change in endpoint_changes),
        "countries_with_decrease_from_first_to_last_year": sum(change < 0 for change in endpoint_changes),
        "countries_unchanged_from_first_to_last_year": sum(change == 0 for change in endpoint_changes),
        "country_level_endpoint_change_min_percentage_points": round(min(endpoint_changes), 4) if endpoint_changes else None,
        "country_level_endpoint_change_max_percentage_points": round(max(endpoint_changes), 4) if endpoint_changes else None,
        "interpretation": (
            "Pooled rates weight reporting countries by interpretable AST count and are not global "
            "population estimates. These summaries are descriptive, not validation or calibration."
        ),
    }
