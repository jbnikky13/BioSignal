from pathlib import Path
import json

import pytest

from biosignal.amrfinder_report import export_evidence, summarize_report, validate_inputs


def test_validate_inputs_requires_matching_gff_protein_ids(tmp_path: Path):
    nucleotide = tmp_path / "genome.fna"
    protein = tmp_path / "protein.faa"
    gff = tmp_path / "genomic.gff"
    nucleotide.write_text(">contig1 description\nATGC\n", encoding="utf-8")
    protein.write_text(">WP_000001.1 protein\nMKK\n", encoding="utf-8")
    gff.write_text(
        "##gff-version 3\n"
        "contig1\tRefSeq\tCDS\t1\t9\t.\t+\t0\tID=cds1;Name=WP_000001.1\n",
        encoding="utf-8",
    )
    assert validate_inputs(nucleotide, protein, gff)["matched_protein_ids"] == 1


def test_validate_inputs_rejects_unmatched_gff_contig(tmp_path: Path):
    nucleotide = tmp_path / "genome.fna"
    protein = tmp_path / "protein.faa"
    gff = tmp_path / "genomic.gff"
    nucleotide.write_text(">contig1\nATGC\n", encoding="utf-8")
    protein.write_text(">WP_000001.1\nMKK\n", encoding="utf-8")
    gff.write_text(
        "other_contig\tRefSeq\tCDS\t1\t9\t.\t+\t0\tID=cds1;Name=WP_000001.1\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="sequence IDs"):
        validate_inputs(nucleotide, protein, gff)


def test_summary_separates_scope_and_flags_internal_stop(tmp_path: Path):
    report = tmp_path / "hits.tsv"
    output = tmp_path / "summary.md"
    report.write_text(
        "Element symbol\tScope\tType\tMethod\tContig id\tStart\tStop\n"
        "blaEC\tplus\tAMR\tBLASTP\tcontig1\t1\t900\n"
        "espX1\tplus\tVIRULENCE\tINTERNAL_STOP\tcontig1\t10\t300\n"
        "gyrA\tcore\tAMR\tPOINT\tcontig1\t400\t500\n",
        encoding="utf-8",
    )
    result = summarize_report(report, output)
    text = output.read_text(encoding="utf-8")
    assert result["report_rows"] == 3
    assert result["scope_counts"] == {"core": 1, "plus": 2}
    assert result["review_flag_rows"] == 1
    assert "phenotypic antimicrobial resistance" in text
    assert "INTERNAL_STOP" in text


def test_export_evidence_keeps_scope_type_loci_and_review_flags(tmp_path: Path):
    report = tmp_path / "hits.tsv"
    output = tmp_path / "evidence.json"
    report.write_text(
        "Protein id\tContig id\tStart\tStop\tElement symbol\tScope\tType\tMethod\t"
        "Closest reference accession\t% Coverage of reference\t% Identity to reference\n"
        "WP_1\tcontig1\t1\t900\tblaEC\tplus\tAMR\tBLASTP\tWP_REF\t100\t98.9\n"
        "WP_2\tcontig1\t10\t300\tespX1\tplus\tVIRULENCE\tINTERNAL_STOP\t.\t.\t.\n"
        "WP_3\tcontig2\t400\t800\tgyrA\tcore\tAMR\tPOINT\tWP_GYR\t100\t100\n",
        encoding="utf-8",
    )

    result = export_evidence(report, output)
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert result["scope_counts"] == {"core": 1, "plus": 2}
    assert result["amr_typed_rows"] == 2
    assert result["review_flag_rows"] == 1
    assert payload["detections"][0]["coverage"] == 100.0
    assert payload["detections"][0]["reference"] == "WP_REF"
    assert payload["detections"][1]["review_required"] is True
    assert payload["detections"][1]["review_reasons"] == ["INTERNAL_STOP"]
    assert payload["detections"][2]["scope"] == "core"
    assert "do not establish phenotypic resistance" in payload["interpretation"]


def test_summary_accepts_header_only_report_as_zero_hits(tmp_path: Path):
    report = tmp_path / "empty.tsv"
    output = tmp_path / "summary.md"
    report.write_text(
        "Element symbol\tScope\tType\tMethod\n",
        encoding="utf-8",
    )
    result = summarize_report(report, output)
    assert result["report_rows"] == 0
    assert "valid empty result" in output.read_text(encoding="utf-8")
