"""Evidence-aware genotype/phenotype linkage.

Only AMRFinderPlus rows explicitly typed AMR are considered AMR genomic
evidence. Aggregate AST proportions remain population-level observations and
are never converted into an individual isolate phenotype.
"""
from dataclasses import dataclass
from .amr import AMRHit
from .models import AMRObservation


@dataclass(frozen=True)
class GenotypePhenotypeLink:
    organism: str
    antimicrobial: str
    phenotype_resistance_rate: float
    genomic_hits: tuple[str, ...]
    genomic_evidence_count: int
    evidence_status: str
    limitations: tuple[str, ...]


def link_evidence(
    observation: AMRObservation,
    hits: list[AMRHit],
    *,
    organism: str,
    antimicrobial: str,
) -> GenotypePhenotypeLink:
    relevant = tuple(
        hit.gene_symbol for hit in hits
        if hit.gene_symbol and hit.is_amr_typed
    )
    limitations = (
        "genomic evidence and phenotype observation are not necessarily from the same isolates",
        "AMR gene or mutation detection does not by itself prove phenotypic resistance",
        "aggregate AST resistance proportions do not establish an individual isolate phenotype",
        "virulence and stress detections are excluded from AMR genomic evidence",
    )
    status = "amr_genomic_evidence_present" if relevant else "no_amr_genomic_evidence"
    return GenotypePhenotypeLink(
        organism=organism,
        antimicrobial=antimicrobial,
        phenotype_resistance_rate=observation.resistance_rate,
        genomic_hits=relevant,
        genomic_evidence_count=len(relevant),
        evidence_status=status,
        limitations=limitations,
    )
