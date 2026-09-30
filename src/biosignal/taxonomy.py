from dataclasses import dataclass

@dataclass(frozen=True)
class TaxonMatch:
    input_name: str
    scientific_name: str | None
    taxid: int | None
    status: str
    matched_alias: str | None = None

SEED_TAXA: dict[str, tuple[str, int]] = {
    "escherichia coli": ("Escherichia coli", 562),
    "e. coli": ("Escherichia coli", 562),
    "klebsiella pneumoniae": ("Klebsiella pneumoniae", 573),
    "k. pneumoniae": ("Klebsiella pneumoniae", 573),
    "staphylococcus aureus": ("Staphylococcus aureus", 1280),
    "s. aureus": ("Staphylococcus aureus", 1280),
    "acinetobacter baumannii": ("Acinetobacter baumannii", 470),
    "a. baumannii": ("Acinetobacter baumannii", 470),
    "pseudomonas aeruginosa": ("Pseudomonas aeruginosa", 287),
    "p. aeruginosa": ("Pseudomonas aeruginosa", 287),
}

def normalize_taxon(name: str) -> TaxonMatch:
    cleaned = " ".join(name.strip().split())
    hit = SEED_TAXA.get(cleaned.casefold())
    if hit:
        scientific_name, taxid = hit
        return TaxonMatch(cleaned, scientific_name, taxid, "resolved", cleaned)
    return TaxonMatch(cleaned, None, None, "unresolved", None)