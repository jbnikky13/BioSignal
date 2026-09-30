"""Evidence-aware genotype/phenotype linkage.

This module joins aggregated phenotype observations to genomic AMR evidence
without treating gene detection as proof of phenotypic resistance.
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
        if hit.gene_symbol and hit.element_type
    )
    limitations = [
        "genomic evidence and phenotype observation are not necessarily from the same isolates",
        "AMR gene detection does not by itself prove phenotypic resistance",
    ]
    if not relevant:
        status = "no_genomic_evidence"
    else:
        status = "genomic_evidence_present"
    return GenotypePhenotypeLink(
        organism=organism,
        antimicrobial=antimicrobial,
        phenotype_resistance_rate=observation.resistance_rate,
        genomic_hits=relevant,
        genomic_evidence_count=len(relevant),
        evidence_status=status,
        limitations=tuple(limitations),
    )
