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


def build_report(
    isolate_id: str,
    organism: str,
    observations: list[AMRObservation],
    hits: list[AMRHit],
    *,
    source: str,
) -> ExperimentReport:
    # Do not present virulence/stress Plus hits as AMR determinants.
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
            "virulence and stress detections are not AMR detections and are excluded from the AMR hit list",
            "aggregate AST observations cannot establish this isolate's phenotype",
            "genotype-phenotype concordance requires verified matching isolate identifiers and compatible antimicrobial evidence",
        ),
        genomic_detections=tuple(hits),
    )


def to_dict(report: ExperimentReport) -> dict:
    """Serialize a report without collapsing scope, element type or review flags."""
    return {
        "isolate_id": report.isolate_id,
        "organism": report.organism,
        "source": report.source,
        "amr_hits": list(report.amr_hits),
        "genomic_detections": [
            {
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
    }
