"""Genomic metadata models and NCBI Datasets command builders."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GenomeRecord:
    accession: str
    organism: str
    taxid: int | None
    assembly_level: str | None = None
    source: str = "NCBI Datasets"


def genome_query(taxon: int | str, *, limit: int = 20, annotated: bool = True) -> list[str]:
    """Build an NCBI Datasets CLI command as an auditable argument list."""
    args = ["datasets", "summary", "genome", "taxon", str(taxon), "--limit", str(limit)]
    if annotated:
        args.append("--annotated")
    args.extend(["--report", "genome"])
    return args


def genome_download_command(
    taxon: int | str,
    *,
    filename: str = "biosignal_genomes.zip",
    limit: int | None = None,
) -> list[str]:
    """Build a bounded genome download command; execution is left to the user/runner."""
    args = [
        "datasets", "download", "genome", "taxon", str(taxon),
        "--include", "genome,gff3,seq-report",
        "--filename", filename,
    ]
    if limit is not None:
        args.extend(["--limit", str(limit)])
    return args
