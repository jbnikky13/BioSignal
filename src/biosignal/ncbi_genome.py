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

def find_assemblies_by_biosample(accession: str) -> list[GenomeAssembly]:
    url = f"{BASE_URL}/genome/biosample/{quote(accession)}/dataset_report"
    request = Request(url, headers={"User-Agent": "BioSignal/0.1 research-client"})
    with urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    assemblies = []
    for record in payload.get("reports", []):
        info = record.get("assembly_info", {})
        organism = record.get("organism", {})
        lineage = info.get("bioproject_lineage") or []
        biosample = info.get("biosample")
        assemblies.append(GenomeAssembly(
            assembly_accession=info.get("assembly_accession", ""),
            assembly_name=info.get("assembly_name"),
            assembly_level=info.get("assembly_level"),
            organism=organism.get("organism_name"),
            biosample_accession=biosample.get("accession") if isinstance(biosample, dict) else None,
            bioproject_accession=lineage[0].get("accession") if lineage else None,
        ))
    return [a for a in assemblies if a.assembly_accession]
