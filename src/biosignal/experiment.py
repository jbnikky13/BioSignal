"""End-to-end evidence report models for a public isolate."""
from dataclasses import dataclass
from .amr import AMRHit
from .models import AMRObservation

@dataclass(frozen=True)
class PhenotypeComparison:
    antimicrobial: str
    phenotype: str
    genomic_evidence: tuple[str, ...]
    interpretation: str

@dataclass(frozen=True)
class ExperimentReport:
    isolate_id: str
    organism: str
    source: str
    amr_hits: tuple[str, ...]
    comparisons: tuple[PhenotypeComparison, ...]
    limitations: tuple[str, ...]

def build_report(isolate_id: str, organism: str, observations: list[AMRObservation], hits: list[AMRHit], *, source: str) -> ExperimentReport:
    hit_names = tuple(sorted({h.gene_symbol for h in hits if h.gene_symbol}))
    comparisons = tuple(
        PhenotypeComparison(
            antimicrobial=o.antimicrobial,
            phenotype="resistant" if o.resistance_rate >= 0.5 else "not_resistant_majority",
            genomic_evidence=hit_names,
            interpretation="genomic evidence is present; this is an evidence comparison, not proof of causality or isolate-level genotype-phenotype concordance",
        ) for o in observations
    )
    return ExperimentReport(
        isolate_id=isolate_id, organism=organism, source=source,
        amr_hits=hit_names, comparisons=comparisons,
        limitations=(
            "genomic and phenotype evidence must be confirmed as originating from the same isolate",
            "AMR gene or mutation detection does not by itself establish phenotypic resistance",
        ),
    )
