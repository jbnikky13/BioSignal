"""Descriptive geographic and temporal summaries for WHO GLASS country-year rows.

These outputs are coverage-aware descriptive statistics, not population estimates,
forecast validation, or operational alerts.
"""
from __future__ import annotations
from collections import defaultdict
from statistics import median
from typing import Any


def summarize_geography_time(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        raise ValueError("rows cannot be empty")

    groups: dict[tuple[str, int, str, str, str], dict[str, Any]] = {}
    country_years: dict[str, set[int]] = defaultdict(set)
    country_regions: dict[str, set[str]] = defaultdict(set)

    for row in rows:
        iso3 = str(row["Iso3"])
        year = int(row["Year"])
        region = str(row["WHORegionName"])
        country_years[iso3].add(year)
        country_regions[iso3].add(region)
        key = (region, year, str(row["Specimen"]), str(row["PathogenName"]), str(row["AbTargets"]))
        group = groups.setdefault(key, {
            "who_region": region, "year": year, "specimen": key[2],
            "pathogen": key[3], "antimicrobial": key[4],
            "resistant_count": 0, "interpretable_ast_count": 0,
            "countries_reporting": 0, "country_percentages": [],
        })
        group["resistant_count"] += int(row["Resistant"])
        group["interpretable_ast_count"] += int(row["InterpretableAST"])
        group["countries_reporting"] += 1
        group["country_percentages"].append(float(row["PercentResistant"]))

    region_year = []
    for key in sorted(groups):
        group = groups[key]
        denominator = group["interpretable_ast_count"]
        region_year.append({
            "who_region": group["who_region"],
            "year": group["year"],
            "specimen": group["specimen"],
            "pathogen": group["pathogen"],
            "antimicrobial": group["antimicrobial"],
            "countries_reporting": group["countries_reporting"],
            "resistant_count": group["resistant_count"],
            "interpretable_ast_count": denominator,
            "pooled_resistance_percent": round(100 * group["resistant_count"] / denominator, 4),
            "median_country_resistance_percent": round(median(group["country_percentages"]), 4),
        })

    country_coverage = [
        {"country_iso3": iso3, "regions_reported": sorted(country_regions[iso3]),
         "years_reported": sorted(years), "year_count": len(years)}
        for iso3, years in sorted(country_years.items())
    ]
    return {
        "region_year": region_year,
        "country_coverage": country_coverage,
        "interpretation": (
            "Regional pooled rates are weighted by reported interpretable AST denominators; "
            "they are descriptive and not population-representative. The median gives each "
            "reporting country equal weight but is not a population estimate. Missing country-years "
            "are not imputed, and WHO regions are not subnational geography."
        ),
    }
