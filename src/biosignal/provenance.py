"""Minimal provenance metadata for imported datasets."""

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class DatasetProvenance:
    source_name: str
    endpoint: str
    retrieved_at: datetime
    row_count: int
    schema_version: str
    transform_version: str

    @classmethod
    def now(
        cls,
        *,
        source_name: str,
        endpoint: str,
        row_count: int,
        schema_version: str = "0.1",
        transform_version: str = "0.1",
    ) -> "DatasetProvenance":
        return cls(
            source_name=source_name,
            endpoint=endpoint,
            retrieved_at=datetime.now(timezone.utc),
            row_count=row_count,
            schema_version=schema_version,
            transform_version=transform_version,
        )
