"""Canonical isolate identity and normalized genomic evidence."""
from dataclasses import dataclass

from .amr import parse_amrfinder_rows


@dataclass(frozen=True)
class IsolateIdentity:
    isolate_id: str
    biosample_accession: str | None = None
    assembly_accession: str | None = None
    sra_accession: str | None = None
    taxid: int | None = None
    organism: str | None = None
    collection_date: str | None = None
    source: str = "public"


@dataclass(frozen=True)
class AMREvidence:
    isolate_id: str
    gene_symbol: str
    evidence_type: str
    method: str
    identity: float | None = None
    coverage: float | None = None
    analysis_version: str | None = None
    reference_catalog_version: str | None = None
    scope: str = "unknown"
    reference: str | None = None
    contig_id: str | None = None
    start: int | None = None
    stop: int | None = None
    review_required: bool = False
    review_reasons: tuple[str, ...] = ()


def canonical_isolate_id(row: dict[str, str]) -> str:
    for key in ("biosample_accession", "BioSample", "assembly_accession", "Assembly", "target_acc", "isolate_id"):
        value = row.get(key)
        if value and value.strip():
            return value.strip()
    raise ValueError("no stable isolate identifier found")


def harmonize_amr_evidence(isolate_id: str, rows: list[dict[str, str]]) -> list[AMREvidence]:
    """Normalize AMRFinderPlus rows while preserving Core/Plus and review state."""
    parsed = parse_amrfinder_rows(rows)
    results: list[AMREvidence] = []
    for hit, row in zip(parsed, rows):
        if not hit.gene_symbol:
            continue
        results.append(AMREvidence(
            isolate_id=isolate_id,
            gene_symbol=hit.gene_symbol,
            evidence_type=hit.element_type,
            method=hit.method,
            identity=hit.identity,
            coverage=hit.coverage,
            analysis_version=_first(row, "AMRFinderPlus version", "amrfinderplus_version") or None,
            reference_catalog_version=_first(row, "Database version", "PD Ref Gene Catalog Version", "refgene_db_version") or None,
            scope=hit.scope,
            reference=hit.reference,
            contig_id=hit.contig_id,
            start=hit.start,
            stop=hit.stop,
            review_required=hit.review_required,
            review_reasons=hit.review_reasons,
        ))
    return results


def _first(row: dict[str, str], *keys: str) -> str:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return str(value).strip()
    return ""
