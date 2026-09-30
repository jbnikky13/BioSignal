from datetime import date
from biosignal.amr import AMRHit
from biosignal.experiment import build_report
from biosignal.models import AMRObservation

def test_builds_reproducible_evidence_report():
    observation = AMRObservation(
        organism="Escherichia coli", antimicrobial="ciprofloxacin",
        period_start=date(2026, 1, 1), period_end=date(2026, 3, 31),
        tested_count=1, resistant_count=1, region="USA",
        source="NCBI BioSample",
    )
    hit = AMRHit("contig-1", "gyrA", "POINT", "AMRFinderPlus", "REF1", 100.0, 99.0)
    report = build_report("SAMN05170351", "Escherichia coli", [observation], [hit], source="NCBI public data")
    assert report.isolate_id == "SAMN05170351"
    assert report.amr_hits == ("gyrA",)
    assert report.comparisons[0].phenotype == "resistant"
    assert "not proof" in report.comparisons[0].interpretation
