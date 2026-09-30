"""Small public NCBI BioSample integration client."""
from dataclasses import dataclass
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json
import xml.etree.ElementTree as ET

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

@dataclass(frozen=True)
class PublicIsolateRecord:
    biosample_accession: str
    organism: str | None
    collection_date: str | None
    geo_loc_name: str | None
    isolation_source: str | None
    bioproject: str | None
    sra_accession: str | None

def _get_json(endpoint: str, params: dict[str, str]) -> dict:
    url = f"{EUTILS}/{endpoint}?{urlencode(params)}"
    request = Request(url, headers={"User-Agent": "BioSignal/0.1 research-client"})
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))

def fetch_biosample(accession: str) -> PublicIsolateRecord:
    search = _get_json("esearch.fcgi", {"db": "biosample", "term": accession, "retmode": "json"})
    ids = search.get("esearchresult", {}).get("idlist", [])
    if not ids:
        raise ValueError(f"BioSample not found: {accession}")
    params = urlencode({"db": "biosample", "id": ids[0], "retmode": "xml"})
    request = Request(f"{EUTILS}/efetch.fcgi?{params}", headers={"User-Agent": "BioSignal/0.1 research-client"})
    with urlopen(request, timeout=20) as response:
        root = ET.fromstring(response.read())
    def text_at(path: str) -> str | None:
        node = root.find(path)
        return node.text.strip() if node is not None and node.text else None
    organism = text_at(".//Organism/Organism_Name")
    attributes = {}
    for attr in root.findall(".//Attribute"):
        name = attr.attrib.get("attribute_name", "").strip().casefold()
        if name and attr.text:
            attributes[name] = attr.text.strip()
    return PublicIsolateRecord(
        biosample_accession=accession,
        organism=organism,
        collection_date=attributes.get("collection date"),
        geo_loc_name=attributes.get("geographic location"),
        isolation_source=attributes.get("isolation source"),
        bioproject=attributes.get("bioproject"),
        sra_accession=attributes.get("sra accession") or attributes.get("sra"),
    )
