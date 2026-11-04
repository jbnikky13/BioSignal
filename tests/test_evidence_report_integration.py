import json
from pathlib import Path

import pytest

from biosignal.amrfinder_report import build_experiment_report


def test_json_evidence_flows_into_unified_report_without_losing_distinctions(tmp_path: Path):
    detections = [
        {
            "sequence_id": "WP_AMR", "gene_symbol": "blaEC", "element_type": "AMR",
            "method": "BLASTP", "reference": "REF_AMR", "coverage": 100.0,
            "identity": 98.5, "scope": "plus", "review_required": False,
            "review_reasons": [], "contig_id": "contig1", "start": 10, "stop": 900,
        },
        {
            "sequence_id": None, "gene_symbol": "nleC", "element_type": "VIRULENCE",
            "method": "INTERNAL_STOP", "reference": None, "coverage": None,
            "identity": None, "scope": "plus", "review_required": True,
            "review_reasons": ["INTERNAL_STOP"], "contig_id": "contig1",
            "start": 1000, "stop": 1300,
        },
        {
            "sequence_id": "WP_STRESS", "gene_symbol": "mdtM", "element_type": "STRESS",
            "method": "BLASTP", "reference": "REF_STRESS", "coverage": 99.0,
            "identity": 97.0, "scope": "plus", "review_required": False,
            "review_reasons": [], "contig_id": "contig1", "start": 1400, "stop": 1700,
        },
        {
            "sequence_id": "WP_CORE", "gene_symbol": "gyrA", "element_type": "AMR",
            "method": "POINT", "reference": "REF_CORE", "coverage": 100.0,
            "identity": 100.0, "scope": "core", "review_required": False,
            "review_reasons": [], "contig_id": "contig2", "start": 10, "stop": 500,
        },
    ]
    evidence = tmp_path / "amrfinderplus_evidence.json"
    evidence.write_text(json.dumps({
        "schema_version": "1.0", "source": "AMRFinderPlus", "row_count": 4,
        "amr_typed_rows": 2, "scope_counts": {"core": 1, "plus": 3},
        "type_counts": {"AMR": 2, "STRESS": 1, "VIRULENCE": 1},
        "review_flag_rows": 1, "detections": detections,
    }), encoding="utf-8")
    out_json, out_md = tmp_path / "experiment_report.json", tmp_path / "experiment_report.md"

    result = build_experiment_report(
        evidence, "SAMN05215988", "Escherichia coli",
        "NCBI BioSample / AMRFinderPlus", out_json, out_md,
    )
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    markdown = out_md.read_text(encoding="utf-8")

    assert result["genomic_detection_rows"] == 4
    assert result["amr_typed_rows"] == 2
    assert result["review_flag_rows"] == 1
    assert payload["amr_hits"] == ["blaEC", "gyrA"]
    assert len(payload["genomic_detections"]) == 4
    assert {row["scope"] for row in payload["genomic_detections"]} == {"core", "plus"}
    assert {row["element_type"] for row in payload["genomic_detections"]} == {
        "AMR", "STRESS", "VIRULENCE"
    }
    nlec = next(row for row in payload["genomic_detections"] if row["gene_symbol"] == "nleC")
    assert nlec["sequence_id"] is None
    assert nlec["review_required"] is True
    assert nlec["review_reasons"] == ["INTERNAL_STOP"]
    assert payload["comparisons"] == []
    assert "No AST phenotype observations were supplied" in markdown
    assert "do not confirm phenotypic resistance" in payload["interpretation"]
    assert "not a clinical or diagnostic interpretation" in markdown
    assert "VIRULENCE" in markdown and "STRESS" in markdown


def test_evidence_loader_rejects_inconsistent_review_counts(tmp_path: Path):
    evidence = tmp_path / "bad.json"
    evidence.write_text(json.dumps({
        "source": "AMRFinderPlus", "row_count": 1, "review_flag_rows": 0,
        "detections": [{
            "gene_symbol": "espX1", "element_type": "VIRULENCE", "scope": "plus",
            "method": "INTERNAL_STOP", "review_required": True,
            "review_reasons": ["INTERNAL_STOP"],
        }],
    }), encoding="utf-8")
    with pytest.raises(ValueError, match="review_flag_rows"):
        build_experiment_report(
            evidence, "SAMN", "E. coli", "test",
            tmp_path / "out.json", tmp_path / "out.md",
        )
