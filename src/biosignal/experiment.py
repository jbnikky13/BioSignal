"""Evidence-aware public-isolate report models.

Aggregate AST observations and isolate-level genomic detections are separate
evidence streams. This module does not infer isolate phenotype from aggregate
resistance proportions or claim genotype-phenotype linkage without identifiers.
"""
from dataclasses import dataclass

from .amr import AMRHit
from .models import AMRObservation


@dataclass(frozen=True)
class PhenotypeComparison:
    antimicrobial: str
    phenotype: str
    genomic_evidence: tuple[str, ...]
    interpretation: str
    resistance_rate: float
    tested_count: int
    resistant_count: int


@dataclass(frozen=True)
class ExperimentReport:
    isolate_id: str
    organism: str
    source: str
    amr_hits: tuple[str, ...]
    comparisons: tuple[PhenotypeComparison, ...]
    limitations: tuple[str, ...]
    genomic_detections: tuple[AMRHit, ...] = ()


def hits_from_evidence_payload(payload: dict) -> list[AMRHit]:
    """Rehydrate AMRFinderPlus JSON while validating its row-level evidence."""
    if payload.get("source") != "AMRFinderPlus":
        raise ValueError("Evidence JSON source must be AMRFinderPlus")
    detections = payload.get("detections")
    if not isinstance(detections, list):
        raise ValueError("Evidence JSON must contain a detections list")
    if payload.get("row_count") != len(detections):
        raise ValueError("Evidence JSON row_count does not match detections length")

    hits: list[AMRHit] = []
    for index, item in enumerate(detections):
        if not isinstance(item, dict):
            raise ValueError(f"Detection {index} must be an object")
        gene = item.get("gene_symbol")
        if not isinstance(gene, str) or not gene.strip():
            raise ValueError(f"Detection {index} has no gene_symbol")
        reasons = item.get("review_reasons") or []
        if not isinstance(reasons, list) or not all(isinstance(reason, str) for reason in reasons):
            raise ValueError(f"Detection {index} has invalid review_reasons")
        review_required = bool(item.get("review_required", False))
        if review_required != bool(reasons):
            raise ValueError(f"Detection {index} review flag/reasons are inconsistent")
        hits.append(AMRHit(
            sequence_id=item.get("sequence_id"),
            gene_symbol=gene.strip(),
            element_type=str(item.get("element_type") or "UNKNOWN").upper(),
            method=str(item.get("method") or "UNKNOWN").upper(),
            reference=item.get("reference"),
            coverage=item.get("coverage"),
            identity=item.get("identity"),
            source=str(item.get("source") or "AMRFinderPlus"),
            scope=str(item.get("scope") or "unknown").lower(),
            element_name=item.get("element_name"),
            subtype=item.get("subtype"),
            class_name=item.get("class_name"),
            subclass=item.get("subclass"),
            contig_id=item.get("contig_id"),
            start=item.get("start"),
            stop=item.get("stop"),
            review_required=review_required,
            review_reasons=tuple(reasons),
        ))
    amr_count = sum(hit.is_amr_typed for hit in hits)
    if payload.get("amr_typed_rows") != amr_count:
        raise ValueError("Evidence JSON amr_typed_rows does not match detection types")
    if payload.get("review_flag_rows") != sum(hit.review_required for hit in hits):
        raise ValueError("Evidence JSON review_flag_rows does not match detection flags")
    scope_counts: dict[str, int] = {}
    type_counts: dict[str, int] = {}
    for hit in hits:
        scope_counts[hit.scope] = scope_counts.get(hit.scope, 0) + 1
        type_counts[hit.element_type] = type_counts.get(hit.element_type, 0) + 1
    if payload.get("scope_counts") != scope_counts:
        raise ValueError("Evidence JSON scope_counts do not match detection scopes")
    if payload.get("type_counts") != type_counts:
        raise ValueError("Evidence JSON type_counts do not match detection types")
    return hits


def build_report(
    isolate_id: str,
    organism: str,
    observations: list[AMRObservation],
    hits: list[AMRHit],
    *,
    source: str,
) -> ExperimentReport:
    # Only rows explicitly typed AMR belong in the AMR-hit list.
    amr_names = tuple(sorted({hit.gene_symbol for hit in hits if hit.gene_symbol and hit.is_amr_typed}))

    # AMRObservation is an aggregate count model and has no isolate key. Therefore
    # its rate cannot be converted into this isolate's resistant/susceptible state.
    comparisons = tuple(
        PhenotypeComparison(
            antimicrobial=observation.antimicrobial,
            phenotype="aggregate_rate_only",
            genomic_evidence=(),
            interpretation=(
                "This is an aggregate AST resistance proportion, not an individual-isolate "
                "phenotype. No genotype-phenotype linkage was made."
            ),
            resistance_rate=observation.resistance_rate,
            tested_count=observation.tested_count,
            resistant_count=observation.resistant_count,
        )
        for observation in observations
    )

    return ExperimentReport(
        isolate_id=isolate_id,
        organism=organism,
        source=source,
        amr_hits=amr_names,
        comparisons=comparisons,
        limitations=(
            "AMRFinderPlus detections are genomic evidence and do not establish phenotypic resistance, expression, or treatment response",
            "Core and Plus scopes are distinct; Plus detections are not automatically clinically relevant resistance determinants",
            "Virulence and stress detections are genomic findings, not AMR detections, and are excluded from the AMR hit list",
            "Aggregate AST observations cannot establish this isolate's phenotype",
            "Genotype-phenotype concordance requires verified matching isolate identifiers and compatible antimicrobial evidence",
            "Rows flagged for manual review must not be treated as confirmed findings until sequence and genomic context are reviewed",
            "This research report is not a clinical or diagnostic interpretation",
        ),
        genomic_detections=tuple(hits),
    )


def to_dict(report: ExperimentReport) -> dict:
    """Serialize a report without collapsing scope, element type or review flags."""
    return {
        "schema_version": "1.0",
        "report_type": "research_evidence_summary",
        "isolate_id": report.isolate_id,
        "organism": report.organism,
        "source": report.source,
        "amr_hits": list(report.amr_hits),
        "genomic_detections": [
            {
                "sequence_id": hit.sequence_id,
                "gene_symbol": hit.gene_symbol,
                "element_type": hit.element_type,
                "scope": hit.scope,
                "method": hit.method,
                "reference": hit.reference,
                "coverage": hit.coverage,
                "identity": hit.identity,
                "contig_id": hit.contig_id,
                "start": hit.start,
                "stop": hit.stop,
                "review_required": hit.review_required,
                "review_reasons": list(hit.review_reasons),
                "is_amr_typed": hit.is_amr_typed,
            }
            for hit in report.genomic_detections
        ],
        "comparisons": [
            {
                "antimicrobial": item.antimicrobial,
                "phenotype": item.phenotype,
                "resistance_rate": item.resistance_rate,
                "tested_count": item.tested_count,
                "resistant_count": item.resistant_count,
                "genomic_evidence": list(item.genomic_evidence),
                "interpretation": item.interpretation,
            }
            for item in report.comparisons
        ],
        "limitations": list(report.limitations),
        "interpretation": (
            "Research evidence summary only. Genomic detections do not confirm phenotypic "
            "resistance, gene expression, or treatment response."
        ),
    }


def render_markdown(report: ExperimentReport) -> str:
    """Render a readable report without flattening evidence categories."""
    lines = [
        "# BioSignal — Public Isolate Evidence Report",
        "",
        f"- **Isolate:** {report.isolate_id}",
        f"- **Organism:** {report.organism}",
        f"- **Source:** {report.source}",
        "- **Report status:** Research evidence summary; not a clinical or diagnostic interpretation",
        "",
        "## AMR-typed genomic detections",
        "",
    ]
    if report.amr_hits:
        lines.extend(f"- {name}" for name in report.amr_hits)
    else:
        lines.append("No AMRFinderPlus rows explicitly typed AMR were reported.")

    lines.extend([
        "",
        "## All genomic detections",
        "",
        "| Gene/element | Type | Scope | Method | Review required | Review reason(s) |",
        "|---|---|---|---|---|---|",
    ])
    for hit in report.genomic_detections:
        reasons = ", ".join(hit.review_reasons) or "—"
        review = "Yes" if hit.review_required else "No"
        lines.append(
            f"| {hit.gene_symbol} | {hit.element_type} | {hit.scope} | "
            f"{hit.method} | {review} | {reasons} |"
        )
    if not report.genomic_detections:
        lines.append("| None | — | — | — | — | — |")

    lines.extend(["", "## Phenotype observations", ""])
    if report.comparisons:
        lines.extend([
            "| Antimicrobial | Evidence level | Resistance proportion | Tested | Resistant | Interpretation |",
            "|---|---|---:|---:|---:|---|",
        ])
        for item in report.comparisons:
            lines.append(
                f"| {item.antimicrobial} | Aggregate only | {item.resistance_rate:.1%} | "
                f"{item.tested_count} | {item.resistant_count} | {item.interpretation} |"
            )
    else:
        lines.append(
            "No AST phenotype observations were supplied to this report. "
            "No isolate-level susceptible/resistant phenotype is assigned."
        )

    lines.extend(["", "## Interpretation limits", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    return "\n".join(lines)
