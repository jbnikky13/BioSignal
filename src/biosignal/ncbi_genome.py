"""NCBI Datasets genome lookup by BioSample accession."""
from dataclasses import dataclass
import json
from urllib.parse import quote
from urllib.request import Request, urlopen

BASE_URL = "https://api.ncbi.nlm.nih.gov/datasets/v2"


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


def find_assemblies_by_biosample(accession: str) -> list[GenomeAssembly]:
    """Resolve a BioSample accession to NCBI genome assembly reports.

    NCBI Datasets v2 returns camelCase report fields such as
    assemblyInfo and assemblyLevel. Parsing also accepts snake_case fields
    so local fixtures and older responses remain usable.
    """
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

        assemblies.append(
            GenomeAssembly(
                assembly_accession=accession_value or "",
                assembly_name=assembly_name,
                assembly_level=assembly_level,
                organism=organism,
                biosample_accession=biosample_accession,
                bioproject_accession=bioproject_accession,
            )
        )

    return [a for a in assemblies if a.assembly_accession]
