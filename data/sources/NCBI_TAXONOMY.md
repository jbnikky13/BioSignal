# NCBI Taxonomy

BioSignal uses NCBI Taxonomy as the normalization target for organism identity.

NCBI Taxonomy provides curated current scientific names, TaxIds, ranks, lineage information, and secondary names/synonyms. BioSignal keeps the original source string, normalized scientific name, and stable TaxId separate.

Unknown names remain unresolved until verified against NCBI Taxonomy. The system does not guess from fuzzy matches.

For production expansion, refresh the registry from NCBI Datasets taxonomy reports/packages and record retrieval/version metadata.

Official documentation:
https://www.ncbi.nlm.nih.gov/datasets/docs/v2/data-processing/taxonomy-processing/taxonomy/
https://www.ncbi.nlm.nih.gov/datasets/docs/v2/how-tos/taxonomy/taxonomy/