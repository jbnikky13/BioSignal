"""CSV ingestion and normalization for aggregated AMR observations."""

import csv
from datetime import date
from pathlib import Path
from typing import Iterable

from .models import AMRObservation


REQUIRED_COLUMNS = {
    "organism",
    "antimicrobial",
    "period_start",
    "period_end",
    "tested_count",
    "resistant_count",
}


def load_csv(path: str | Path) -> list[AMRObservation]:
    """Load a CSV containing aggregated AMR observations."""
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")

        return [row_to_observation(row) for row in reader]


def row_to_observation(row: dict[str, str]) -> AMRObservation:
    """Normalize one CSV row into the canonical BioSignal schema."""
    return AMRObservation(
        organism=row["organism"].strip(),
        antimicrobial=row["antimicrobial"].strip(),
        period_start=date.fromisoformat(row["period_start"]),
        period_end=date.fromisoformat(row["period_end"]),
        tested_count=int(row["tested_count"]),
        resistant_count=int(row["resistant_count"]),
        region=_optional(row.get("region")),
        source=_optional(row.get("source")),
    )


def _optional(value: str | None) -> str | None:
    return value.strip() if value and value.strip() else None


def iter_observations(rows: Iterable[dict[str, str]]) -> Iterable[AMRObservation]:
    """Convert iterable CSV-style rows without materializing the dataset."""
    for row in rows:
        yield row_to_observation(row)
