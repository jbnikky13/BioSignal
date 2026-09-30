"""Structured ingestion of AMRFinderPlus-style tabular results.

BioSignal does not implement its own AMR classifier here. NCBI's AMRFinderPlus
uses curated reference genes/HMMs and can identify AMR genes and resistance-
associated point mutations. This module normalizes its output for provenance
and downstream analysis.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class AMRHit:
    sequence_id: str
    gene_symbol: str
    element_type: str
    method: str
    reference: str | None
    coverage: float | None
    identity: float | None
    source: str = "AMRFinderPlus"


def parse_amrfinder_rows(rows: list[dict[str, str]]) -> list[AMRHit]:
    hits = []
    for row in rows:
        hits.append(AMRHit(
            sequence_id=row.get("Protein identifier") or row.get("Contig id") or "",
            gene_symbol=row.get("Element symbol", ""),
            element_type=row.get("Type", ""),
            method=row.get("Method", ""),
            reference=row.get("Reference sequence accession", None),
            coverage=_float(row.get("% Coverage of reference sequence")),
            identity=_float(row.get("% Identity to reference sequence")),
        ))
    return hits


def _float(value: str | None) -> float | None:
    if value in (None, "", "."):
        return None
    return float(value)
