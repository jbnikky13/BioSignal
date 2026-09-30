from datetime import date
from biosignal.amr import AMRHit
from biosignal.linkage import link_evidence
from biosignal.models import AMRObservation


def test_linkage_keeps_genomic_evidence_separate_from_phenotype():
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
    hit = AMRHit(
        sequence_id="contig-1",
        gene_symbol="gyrA",
        element_type="POINT",
        method="AMRFinderPlus",
        reference="REF1",
        coverage=100.0,
        identity=99.0,
    )
    result = link_evidence(
        observation,
        [hit],
        organism="Escherichia coli",
        antimicrobial="ciprofloxacin",
    )
    assert result.phenotype_resistance_rate == 0.30
    assert result.genomic_hits == ("gyrA",)
    assert result.evidence_status == "genomic_evidence_present"
    assert "does not by itself prove" in result.limitations[1]
