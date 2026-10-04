"""NCBI Datasets genome lookup by BioSample accession."""
from dataclasses import dataclass
import json
import re
from urllib.parse import quote
from urllib.request import Request, urlopen

BASE_URL = "https://api.ncbi.nlm.nih.gov/datasets/v2"
BIOSAMPLE_RE = re.compile(r"^SAMN[0-9]+$")


@dataclass(frozen=True)
class GenomeAssembly:
    assembly_accession: str
    assembly_name: str | None
    assembly_level: str | None
    organism: str | None
    biosample_accession: str | None
    bioproject_accession: str | None


def _first(value, *keys, default=None):
    if not isinstance(value, dict):
        return default
    for key in keys:
        if key in value and value[key] not in (None, ""):
            return value[key]
    return default


def _assembly_rank(assembly: GenomeAssembly) -> tuple[int, int, str]:
    """Prefer more complete and RefSeq-backed assemblies deterministically."""
    levels = {
        "complete": 0,
        "chromosome": 1,
        "scaffold": 2,
        "contig": 3,
    }
    level = (assembly.assembly_level or "").strip().casefold()
    completeness = next((rank for name, rank in levels.items() if name in level), 9)
    refseq_penalty = 0 if assembly.assembly_accession.startswith("GCF_") else 1
    return completeness, refseq_penalty, assembly.assembly_accession


def find_assemblies_by_biosample(accession: str) -> list[GenomeAssembly]:
    """Resolve a BioSample accession to NCBI genome assembly reports."""
    accession = accession.strip().upper()
    if not BIOSAMPLE_RE.fullmatch(accession):
        raise ValueError(f"invalid BioSample accession: {accession!r}")

    url = f"{BASE_URL}/genome/biosample/{quote(accession)}/dataset_report"
    request = Request(url, headers={"User-Agent": "BioSignal/0.1 research-client"})
    with urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))

    reports = payload.get("reports", [])
    if isinstance(reports, dict):
        reports = reports.get("reports", [])

    assemblies = []
    for record in reports:
        if not isinstance(record, dict):
            continue

        info = _first(record, "assemblyInfo", "assembly_info", default={}) or {}
        organism_info = _first(record, "organism", default={}) or {}

        accession_value = _first(
            record,
            "accession",
            "assembly_accession",
            default=_first(info, "assemblyAccession", "assembly_accession"),
        )
        assembly_name = _first(info, "assemblyName", "assembly_name")
        assembly_level = _first(info, "assemblyLevel", "assembly_level")

        organism = _first(organism_info, "organismName", "organism_name")
        if organism is None and isinstance(organism_info, str):
            organism = organism_info

        biosample = _first(info, "biosample", default={}) or {}
        biosample_accession = _first(
            biosample, "accession", "biosample_accession"
        )

        bioproject_accession = _first(
            info, "bioprojectAccession", "bioproject_accession"
        )
        if bioproject_accession is None:
            lineage = _first(
                info, "bioprojectLineage", "bioproject_lineage", default=[]
            ) or []
            if lineage and isinstance(lineage[0], dict):
                projects = lineage[0].get("bioprojects") or []
                if projects and isinstance(projects[0], dict):
                    bioproject_accession = _first(projects[0], "accession")

        assembly = GenomeAssembly(
            assembly_accession=accession_value or "",
            assembly_name=assembly_name,
            assembly_level=assembly_level,
            organism=organism,
            biosample_accession=biosample_accession,
            bioproject_accession=bioproject_accession,
        )
        if assembly.biosample_accession and assembly.biosample_accession.upper() != accession:
            continue
        assemblies.append(assembly)

    return sorted(
        (a for a in assemblies if a.assembly_accession),
        key=_assembly_rank,
    )
