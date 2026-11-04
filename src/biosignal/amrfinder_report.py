"""Validation and transparent summaries for AMRFinderPlus evidence."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from dataclasses import asdict
import json
from pathlib import Path
from urllib.parse import unquote

from .amr import parse_amrfinder_rows


def fasta_ids(path: Path) -> set[str]:
    identifiers = set()
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.startswith(">"):
                identifiers.add(line[1:].strip().split()[0])
    if not identifiers:
        raise ValueError(f"No FASTA records found: {path}")
    return identifiers


def validate_inputs(nucleotide: Path, protein: Path, gff: Path) -> dict[str, int]:
    nucleotide_ids = fasta_ids(nucleotide)
    protein_ids = fasta_ids(protein)
    gff_contigs: set[str] = set()
    gff_proteins: set[str] = set()
    with gff.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip() or line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) != 9:
                raise ValueError(f"GFF line {line_number} has {len(fields)} columns, expected 9")
            if fields[2] not in {"CDS", "gene"}:
                continue
            gff_contigs.add(fields[0])
            attributes = {}
            for item in fields[8].split(";"):
                if "=" in item:
                    key, value = item.split("=", 1)
                    attributes[key] = unquote(value)
            if attributes.get("Name"):
                gff_proteins.add(attributes["Name"])
    if not gff_contigs:
        raise ValueError("GFF contains no CDS/gene feature rows")
    unknown = gff_contigs - nucleotide_ids
    if unknown:
        raise ValueError(f"GFF sequence IDs do not match nucleotide FASTA: {sorted(unknown)[:5]}")
    matched = protein_ids & gff_proteins
    if not matched:
        raise ValueError("No GFF Name= identifiers match protein FASTA record IDs")
    return {
        "nucleotide_contigs": len(nucleotide_ids),
        "protein_records": len(protein_ids),
        "gff_feature_ids": len(gff_proteins),
        "matched_protein_ids": len(matched),
    }


def _read_report(report: Path) -> list[dict[str, str]]:
    with report.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        required = {"Element symbol", "Scope", "Type", "Method"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"AMRFinderPlus TSV missing required columns: {sorted(required)}")
        return list(reader)


def summarize_report(report: Path, output: Path) -> dict:
    rows = _read_report(report)
    scopes = Counter((row["Scope"] or "UNKNOWN").strip().lower() for row in rows)
    types = Counter((row["Type"] or "UNKNOWN").strip().upper() for row in rows)
    methods = Counter((row["Method"] or "UNKNOWN").strip().upper() for row in rows)
    symbols = Counter(row["Element symbol"] or "UNKNOWN" for row in rows)
    review_methods = {"INTERNAL_STOP", "PARTIAL", "PARTIAL_CONTIG_END"}
    review_rows = [row for row in rows if (row["Method"] or "").strip().upper() in review_methods]

    lines = [
        "# AMRFinderPlus combined-analysis summary",
        "",
        f"- Report rows: **{len(rows)}**",
        f"- Unique element symbols: **{len(symbols)}**",
        "",
        "## Scope counts",
        "",
        "| Scope | Rows |",
        "|---|---:|",
    ]
    lines.extend(
        f"| {key} | {value} |" for key, value in sorted(scopes.items())
    ) if rows else lines.append("| None | 0 |")
    lines.extend(["", "## Type counts", "", "| Type | Rows |", "|---|---:|"])
    lines.extend(
        f"| {key} | {value} |" for key, value in sorted(types.items())
    ) if rows else lines.append("| None | 0 |")
    lines.extend(["", "## Detection-method counts", "", "| Method | Rows |", "|---|---:|"])
    lines.extend(
        f"| {key} | {value} |" for key, value in sorted(methods.items())
    ) if rows else lines.append("| None | 0 |")

    lines.extend(["", "## Review flags", ""])
    if review_rows:
        lines.extend([
            "The following rows warrant manual sequence/context review:",
            "",
            "| Element | Scope | Type | Method | Contig | Start | Stop |",
            "|---|---|---|---|---|---:|---:|",
        ])
        for row in review_rows:
            lines.append(
                f"| {row.get('Element symbol', '')} | {row.get('Scope', '')} | "
                f"{row.get('Type', '')} | {row.get('Method', '')} | "
                f"{row.get('Contig id', '')} | {row.get('Start', '')} | {row.get('Stop', '')} |"
            )
    elif rows:
        lines.append("No INTERNAL_STOP or partial-alignment methods were reported.")
    else:
        lines.append(
            "No elements were reported by AMRFinderPlus for this assembly. "
            "This is a valid empty result, not evidence that the organism is universally susceptible."
        )

    lines.extend([
        "",
        "## Interpretation limits",
        "",
        "- Core and Plus scopes are reported separately; Plus-scope detections are not equivalent to confirmed clinically relevant resistance determinants.",
        "- A detected gene or mutation does not establish phenotypic antimicrobial resistance, gene expression, or clinical treatment response.",
        "- Duplicate element symbols can represent distinct genomic loci and are retained as separate report rows.",
        "- Method, identity, reference coverage, and genomic context should be reviewed before biological interpretation.",
        "- This is an automated evidence summary, not a clinical or diagnostic interpretation.",
        "",
    ])
    output.write_text("\n".join(lines), encoding="utf-8")
    return {
        "report_rows": len(rows),
        "unique_element_symbols": len(symbols),
        "scope_counts": dict(sorted(scopes.items())),
        "type_counts": dict(sorted(types.items())),
        "method_counts": dict(sorted(methods.items())),
        "review_flag_rows": len(review_rows),
    }


def export_evidence(report: Path, output: Path) -> dict:
    """Write normalized row-level evidence without collapsing loci or scope."""
    rows = _read_report(report)
    detections = []
    for hit in parse_amrfinder_rows(rows):
        item = asdict(hit)
        item["is_amr_typed"] = hit.is_amr_typed
        detections.append(item)
    payload = {
        "schema_version": "1.0",
        "source": "AMRFinderPlus",
        "row_count": len(detections),
        "amr_typed_rows": sum(item["is_amr_typed"] for item in detections),
        "scope_counts": dict(sorted(Counter(item["scope"] for item in detections).items())),
        "type_counts": dict(sorted(Counter(item["element_type"] for item in detections).items())),
        "review_flag_rows": sum(item["review_required"] for item in detections),
        "detections": detections,
        "interpretation": (
            "Genomic detections are evidence only; they do not establish phenotypic resistance, "
            "expression, or treatment response."
        ),
    }
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return {key: payload[key] for key in (
        "row_count", "amr_typed_rows", "scope_counts", "type_counts", "review_flag_rows"
    )}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate-inputs")
    validate.add_argument("--nucleotide", type=Path, required=True)
    validate.add_argument("--protein", type=Path, required=True)
    validate.add_argument("--gff", type=Path, required=True)
    summary = sub.add_parser("summarize")
    summary.add_argument("--report", type=Path, required=True)
    summary.add_argument("--output", type=Path, required=True)
    export = sub.add_parser("export-evidence")
    export.add_argument("--report", type=Path, required=True)
    export.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "validate-inputs":
        print(validate_inputs(args.nucleotide, args.protein, args.gff))
    elif args.command == "summarize":
        print(summarize_report(args.report, args.output))
    else:
        print(export_evidence(args.report, args.output))


if __name__ == "__main__":
    main()
