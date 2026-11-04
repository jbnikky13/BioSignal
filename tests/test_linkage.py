from datetime import date

from biosignal.amr import AMRHit
from biosignal.linkage import link_evidence
from biosignal.models import AMRObservation


def test_linkage_includes_only_explicit_amr_typed_rows():
    observation = AMRObservation(
        organism="Escherichia coli",
        antimicrobial="ciprofloxacin",
        period_start=date(2026, 1, 1),
        period_end=date(2026, 3, 31),
        tested_count=100,
        resistant_count=30,
        region="Nigeria",
        source="WHO GLASS-AMR",
    )
    hits = [
        AMRHit("WP_1", "gyrA", "AMR", "POINT", "REF1", 100.0, 99.0, scope="core"),
        AMRHit("WP_2", "espX1", "VIRULENCE", "INTERNAL_STOP", None, None, None,
               scope="plus", review_required=True, review_reasons=("INTERNAL_STOP",)),
        AMRHit("WP_3", "mdtM", "STRESS", "BLASTP", "REF3", 98.0, 97.0, scope="plus"),
    ]
    result = link_evidence(
        observation, hits, organism="Escherichia coli", antimicrobial="ciprofloxacin"
    )
    assert result.phenotype_resistance_rate == 0.30
    assert result.genomic_hits == ("gyrA",)
    assert result.genomic_evidence_count == 1
    assert result.evidence_status == "amr_genomic_evidence_present"
    assert any("not necessarily from the same isolates" in item for item in result.limitations)
    assert any("aggregate AST" in item for item in result.limitations)


def test_linkage_does_not_treat_virulence_or_stress_as_amr_evidence():
    observation = AMRObservation(
        organism="Escherichia coli",
        antimicrobial="ceftriaxone",
        period_start=date(2026, 1, 1),
        period_end=date(2026, 3, 31),
        tested_count=20,
        resistant_count=5,
        region="Nigeria",
        source="aggregate surveillance",
    )
    hits = [
        AMRHit("WP_1", "eae", "VIRULENCE", "BLASTP", None, None, None),
        AMRHit("WP_2", "acrF", "STRESS", "BLASTP", None, None, None),
    ]
    result = link_evidence(
        observation, hits, organism="Escherichia coli", antimicrobial="ceftriaxone"
    )
    assert result.genomic_hits == ()
    assert result.genomic_evidence_count == 0
    assert result.evidence_status == "no_amr_genomic_evidence"
