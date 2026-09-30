# NCBI genomic data

BioSignal uses NCBI Datasets as the genomic-data access layer.

NCBI Datasets can retrieve genome packages by taxonomy ID or name and can include genomic sequence, annotation and sequence reports. BioSignal starts with bounded metadata queries before downloading sequence data.

The project also documents NCBI Pathogen Detection as a future AMR-genomics integration. NCBI's pathogen pipeline assembles pathogen sequence reads, clusters genomes, reconstructs SNP-based phylogenetic relationships, and identifies AMR genes/proteins using AMRFinderPlus.

BioSignal will not infer resistance from sequence similarity alone. Genomic AMR claims should be tied to curated reference annotations and documented methods.

Official sources:
- NCBI Datasets: https://www.ncbi.nlm.nih.gov/datasets/
- Genome downloads: https://www.ncbi.nlm.nih.gov/datasets/docs/v2/how-tos/genomes/download-genome/
- Pathogen Detection: https://www.ncbi.nlm.nih.gov/pathogens/docs/data_processing/
- AMR resources: https://www.ncbi.nlm.nih.gov/pathogens/antimicrobial-resistance/
