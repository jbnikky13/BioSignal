#!/usr/bin/env python3
"""Validate NCBI genome annotation inputs and summarize AMRFinderPlus TSV output."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
from urllib.parse import unquote


def fasta_ids(path: Path) -> set[str]:
    ids = set()
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.startswith(">"):
                ids.add(line[1:].strip().split()[0])
    if not ids:
        raise ValueError(f"No FASTA records found: {path}")
    return ids


def validate_inputs(nucleotide: Path, protein: Path, gff: Path) -> dict[str, int]:
    nucleotide_ids = fasta_ids(nucleotide)
    protein_ids = fasta_ids(protein)
    gff_seqids: set[str] = set()
    gff_protein_ids: set[str] = set()
    with gff.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip() or line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) != 9:
                raise ValueError(f"GFF line {line_number} has {len(fields)} columns, expected 9")
            if fields[2] not in {"CDS", "gene"}:
                continue
            gff_seqids.add(fields[0])
            attrs = {}
            for item in fields[8].split(";"):
                if "=" in item:
                    key, value = item.split("=", 1)
                    attrs[key] = unquote(value)
            if attrs.get("Name"):
                gff_protein_ids.add(attrs["Name"])
    if not gff_seqids:
        raise ValueError("GFF contains no CDS/gene feature rows")
    unknown_contigs = gff_seqids - nucleotide_ids
    if unknown_contigs:
        sample = sorted(unknown_contigs)[:5]
        raise ValueError(f"GFF sequence IDs do not match nucleotide FASTA: {sample}")
    matched = protein_ids & gff_protein_ids
    if not matched:
        raise ValueError("No GFF Name= identifiers match protein FASTA record IDs")
    return {
        "nucleotide_contigs": len(nucleotide_ids),
        "protein_records": len(protein_ids),
        "gff_feature_ids": len(gff_protein_ids),
        "matched_protein_ids": len(matched),
    }


def summarize_report(report: Path, output: Path) -> dict:
    with report.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        required = {"Element symbol", "Scope", "Type", "Method"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"AMRFinderPlus TSV missing required columns: {sorted(required)}")
        rows = list(reader)
    if not rows:
        raise ValueError("AMRFinderPlus report contains no data rows")
    scopes = Counter(row["Scope"] or "UNKNOWN" for row in rows)
    types = Counter(row["Type"] or "UNKNOWN" for row in rows)
    methods = Counter(row["Method"] or "UNKNOWN" for row in rows)
    symbols = Counter(row["Element symbol"] or "UNKNOWN" for row in rows)
    caution_methods = {"INTERNAL_STOP", "PARTIAL", "PARTIAL_CONTIG_END"}
    caution_rows = [
        row for row in rows
        if row["Method"] in caution_methods
    ]
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
    if rows:\n        lines.extend(f"| {key} | {value} |" for key, value in sorted(scopes.items()))\n    else:\n        lines.append("| None | 0 |")
    lines += ["", "## Type counts", "", "| Type | Rows |", "|---|---:|"]
    if rows:\n        lines.extend(f"| {key} | {value} |" for key, value in sorted(types.items()))\n    else:\n        lines.append("| None | 0 |")
    lines += ["", "## Detection-method counts", "", "| Method | Rows |", "|---|---:|"]
    if rows:\n        lines.extend(f"| {key} | {value} |" for key, value in sorted(methods.items()))\n    else:\n        lines.append("| None | 0 |")
    lines += ["", "## Review flags", ""]
    if caution_rows:
        lines.append("The following rows use methods that warrant manual sequence/context review:")
        lines.append("")
        lines.append("| Element | Scope | Type | Method | Contig | Start | Stop |")
        lines.append("|---|---|---|---|---|---:|---:|")
        for row in caution_rows:
            lines.append(
                f"| {row.get('Element symbol', '')} | {row.get('Scope', '')} | "
                f"{row.get('Type', '')} | {row.get('Method', '')} | "
                f"{row.get('Contig id', '')} | {row.get('Start', '')} | {row.get('Stop', '')} |"
            )
    else:
        lines.append("No INTERNAL_STOP or partial-alignment methods were reported.")
    lines += [
        "",
        "## Interpretation limits",
        "",
        "- Core and Plus scopes are reported separately; Plus-scope detections are not equivalent to confirmed clinically relevant resistance determinants.",
        "- A detected gene or mutation does not establish phenotypic antimicrobial resistance, gene expression, or clinical treatment response.",
        "- Duplicate element symbols can represent distinct genomic loci and are retained as separate report rows.",
        "- Method, identity, reference coverage, and genomic context should be reviewed before biological interpretation.",
        "- This is an automated evidence summary, not a clinical or diagnostic interpretation.",
        "",
    ]
    output.write_text("\n".join(lines), encoding="utf-8")
    return {
        "report_rows": len(rows),
        "unique_element_symbols": len(symbols),
        "scope_counts": dict(sorted(scopes.items())),
        "type_counts": dict(sorted(types.items())),
        "method_counts": dict(sorted(methods.items())),
        "review_flag_rows": len(caution_rows),
    }


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
    args = parser.parse_args()
    if args.command == "validate-inputs":
        print(validate_inputs(args.nucleotide, args.protein, args.gff))
    else:
        print(summarize_report(args.report, args.output))


if __name__ == "__main__":
    main()
