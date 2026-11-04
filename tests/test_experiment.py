from datetime import date

from biosignal.amr import AMRHit, parse_amrfinder_rows
from biosignal.experiment import build_report, to_dict
from biosignal.models import AMRObservation


def test_aggregate_ast_is_not_reported_as_isolate_phenotype():
    observation = AMRObservation(
        organism="Escherichia coli", antimicrobial="ciprofloxacin",
        period_start=date(2026, 1, 1), period_end=date(2026, 3, 31),
        tested_count=100, resistant_count=75, region="USA",
        source="aggregate surveillance",
    )
    hits = parse_amrfinder_rows([
        {"Element symbol": "blaEC", "Type": "AMR", "Scope": "plus", "Method": "BLASTP"},
        {"Element symbol": "espX1", "Type": "VIRULENCE", "Scope": "plus", "Method": "INTERNAL_STOP"},
        {"Element symbol": "gyrA", "Type": "AMR", "Scope": "core", "Method": "POINT"},
    ])
    report = build_report("SAMN123", "Escherichia coli", [observation], hits, source="NCBI public data")

    assert report.amr_hits == ("blaEC", "gyrA")
    assert report.comparisons[0].phenotype == "aggregate_rate_only"
    assert report.comparisons[0].resistance_rate == 0.75
    assert report.comparisons[0].genomic_evidence == ()
    assert "not an individual-isolate" in report.comparisons[0].interpretation
    assert len(report.genomic_detections) == 3

    serialized = to_dict(report)
    assert {item["scope"] for item in serialized["genomic_detections"]} == {"core", "plus"}
    esp = next(item for item in serialized["genomic_detections"] if item["gene_symbol"] == "espX1")
    assert esp["element_type"] == "VIRULENCE"
    assert esp["review_required"] is True
    assert esp["review_reasons"] == ["INTERNAL_STOP"]
    assert serialized["comparisons"][0]["phenotype"] == "aggregate_rate_only"


def test_report_does_not_call_virulence_only_hit_an_amr_hit():
    virulence = AMRHit("contig1", "eae", "VIRULENCE", "BLASTP", None, None, None, scope="plus")
    report = build_report("SAMN123", "E. coli", [], [virulence], source="test")
    assert report.amr_hits == ()
    assert report.genomic_detections == (virulence,)
