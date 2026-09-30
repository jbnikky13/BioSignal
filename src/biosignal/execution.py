"""Downloadable NCBI genome/AMR execution plan.

The module deliberately separates network retrieval from analysis execution.
It creates a manifest that can be reviewed and then consumed by a pinned
AMRFinderPlus/Nextflow run. No patient data are involved.
"""
from dataclasses import dataclass
import json
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

DATASETS_URL = "https://api.ncbi.nlm.nih.gov/datasets/v2"


@dataclass(frozen=True)
class AssemblyManifest:
    biosample_accession: str
    assembly_accession: str
    organism: str | None
    assembly_level: str | None
    source: str = "NCBI Datasets v2"


def write_manifest(manifest: AssemblyManifest, output: str | Path) -> Path:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "biosample_accession": manifest.biosample_accession,
        "assembly_accession": manifest.assembly_accession,
        "organism": manifest.organism,
        "assembly_level": manifest.assembly_level,
        "source": manifest.source,
    }, indent=2) + "\n", encoding="utf-8")
    return path


def build_manifest_from_assembly(assembly, biosample_accession: str) -> AssemblyManifest:
    if not assembly.assembly_accession:
        raise ValueError("assembly accession is required")
    return AssemblyManifest(
        biosample_accession=biosample_accession,
        assembly_accession=assembly.assembly_accession,
        organism=assembly.organism,
        assembly_level=assembly.assembly_level,
    )
