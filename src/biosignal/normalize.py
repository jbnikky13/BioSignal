"""Normalize surveillance rows into BioSignal's canonical observation model."""
from datetime import date
from .models import AMRObservation

def normalize_row(
    row: dict[str, str],
    *,
    organism: str,
    antimicrobial: str,
    region: str | None = None,
    source: str = "WHO GLASS-AMR",
    period_start_column: str = "PERIOD_START",
    period_end_column: str = "PERIOD_END",
    tested_count_column: str = "TESTED_COUNT",
    resistant_count_column: str = "RESISTANT_COUNT",
    specimen_type_column: str = "SPECIMEN_TYPE",
    testing_criteria_column: str = "TESTING_CRITERIA",
    laboratory_method_column: str = "LABORATORY_METHOD",
) -> AMRObservation:
    """Convert an explicitly mapped source row into a BioSignal observation.

    Source-specific code/label mappings must happen before this function.
    """
    return AMRObservation(
        organism=organism.strip(),
        antimicrobial=antimicrobial.strip(),
        period_start=date.fromisoformat(row[period_start_column]),
        period_end=date.fromisoformat(row[period_end_column]),
        tested_count=int(row[tested_count_column]),
        resistant_count=int(row[resistant_count_column]),
        region=region.strip() if region else None,
        source=source,
        specimen_type=_optional(row.get(specimen_type_column)),
        testing_criteria=_optional(row.get(testing_criteria_column)),
        laboratory_method=_optional(row.get(laboratory_method_column)),
    )


def _optional(value: str | None) -> str | None:
    """Return normalized optional metadata without inferring missing values."""
    return value.strip() if value and value.strip() else None
