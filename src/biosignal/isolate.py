from dataclasses import dataclass

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

def canonical_isolate_id(row: dict[str, str]) -> str:
    for key in ("biosample_accession", "BioSample", "assembly_accession", "Assembly", "target_acc", "isolate_id"):
        value = row.get(key)
        if value and value.strip():
            return value.strip()
    raise ValueError("no stable isolate identifier found")

def harmonize_amr_evidence(isolate_id: str, rows: list[dict[str, str]]) -> list[AMREvidence]:
    results = []
    for row in rows:
        gene = row.get("Element symbol") or row.get("element_symbol") or ""
        if not gene:
            continue
        results.append(AMREvidence(isolate_id=isolate_id, gene_symbol=gene, evidence_type=(row.get("Type") or row.get("type") or "UNKNOWN").upper(), method=row.get("Method") or row.get("amr_method") or "UNKNOWN", identity=_number(row.get("% Identity") or row.get("pct_ref_identity")), coverage=_number(row.get("% Coverage") or row.get("pct_ref_coverage")), analysis_version=row.get("AMRFinderPlus version") or row.get("amrfinderplus_version"), reference_catalog_version=row.get("PD Ref Gene Catalog Version") or row.get("refgene_db_version")))
    return results

def _number(value: str | None) -> float | None:
    if value in (None, "", "."):
        return None
    return float(value)
