"""Structured ingestion of AMRFinderPlus tabular evidence.

AMRFinderPlus detections are genomic evidence, not phenotype calls. Scope,
element type, method, coordinates and review flags are retained separately.
"""
from dataclasses import dataclass


_REVIEW_METHODS = {"INTERNAL_STOP", "PARTIAL", "PARTIAL_CONTIG_END"}


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
    scope: str = "unknown"
    element_name: str | None = None
    subtype: str | None = None
    class_name: str | None = None
    subclass: str | None = None
    contig_id: str | None = None
    start: int | None = None
    stop: int | None = None
    review_required: bool = False
    review_reasons: tuple[str, ...] = ()

    @property
    def is_amr_typed(self) -> bool:
        """True only for AMRFinderPlus rows explicitly typed AMR."""
        return self.element_type.strip().upper() == "AMR"


def parse_amrfinder_rows(rows: list[dict[str, str]]) -> list[AMRHit]:
    """Parse current and legacy AMRFinderPlus TSV headers without losing scope."""
    hits: list[AMRHit] = []
    for row in rows:
        method = _first(row, "Method", "method").strip().upper() or "UNKNOWN"
        reasons = (method,) if method in _REVIEW_METHODS else ()
        hits.append(AMRHit(
            sequence_id=_first(row, "Protein id", "Protein identifier", "Contig id"),
            gene_symbol=_first(row, "Element symbol", "element_symbol"),
            element_type=_first(row, "Type", "type").strip().upper() or "UNKNOWN",
            method=method,
            reference=_optional(_first(row, "Closest reference accession", "Reference sequence accession")),
            coverage=_float(_first(row, "% Coverage of reference", "% Coverage of reference sequence", "% Coverage")),
            identity=_float(_first(row, "% Identity to reference", "% Identity to reference sequence", "% Identity")),
            scope=_first(row, "Scope", "scope").strip().lower() or "unknown",
            element_name=_optional(_first(row, "Element name")),
            subtype=_optional(_first(row, "Subtype")),
            class_name=_optional(_first(row, "Class")),
            subclass=_optional(_first(row, "Subclass")),
            contig_id=_optional(_first(row, "Contig id")),
            start=_int(_first(row, "Start")),
            stop=_int(_first(row, "Stop")),
            review_required=bool(reasons),
            review_reasons=reasons,
        ))
    return hits


def _first(row: dict[str, str], *keys: str) -> str:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return str(value)
    return ""


def _optional(value: str) -> str | None:
    value = value.strip()
    return value if value and value != "." else None


def _float(value: str) -> float | None:
    value = value.strip()
    if value in ("", "."):
        return None
    return float(value)


def _int(value: str) -> int | None:
    value = value.strip()
    if value in ("", "."):
        return None
    return int(value)
