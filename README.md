# BioSignal

**Biological health intelligence for pathogen surveillance and antimicrobial-resistance signals.**

BioSignal is an open-source research and engineering project for turning aggregated biological and clinical observations into explainable signals about pathogens, antimicrobial resistance (AMR), and temporal/geographic trends.

> **Core principle:** intelligence, not identities.

## Current status

**Phase 3 — Bioinformatics: IN PROGRESS**

The project has completed the foundation and core data-engineering layers and is now building the first reproducible pathogen-genomics workflow.

### Pipeline

Public / permitted data  
→ ingestion  
→ normalization  
→ provenance  
→ data-quality assessment  
→ pathogen taxonomy  
→ genomic metadata  
→ FASTA sequence parsing  
→ sequence QC  
→ genomic annotation  
→ AMR intelligence

## Completed

### Phase 1 — Foundation
- [x] Repository architecture
- [x] Canonical AMR observation schema
- [x] Deterministic resistance signal engine
- [x] Unit tests
- [x] Public data-source definitions

### Phase 2 — Data engineering
- [x] CSV ingestion
- [x] WHO GLASS-AMR query builder
- [x] Runtime public-data fetcher
- [x] Dataset provenance
- [x] Data-quality assessment
- [x] Explicit source-to-canonical normalization layer

### Phase 3 — Bioinformatics — IN PROGRESS
- [x] Pathogen taxonomy normalization with NCBI TaxIDs
- [x] NCBI genomic metadata/query layer
- [x] FASTA parser
- [x] Basic sequence QC
- [x] FASTQ support
- [x] Genome feature extraction
- [x] AMR result ingestion layer
- [ ] Genotype/phenotype linkage
- [ ] Reproducible Nextflow/Snakemake workflow

### Phase 4 — Intelligence
- [ ] Temporal anomaly detection
- [ ] Geographic aggregation
- [ ] AMR trend analysis
- [ ] Genomic resistance-marker analysis
- [ ] Genotype/phenotype relationship analysis
- [ ] Signal calibration against published surveillance metrics

### Phase 5 — Interface
- [ ] Research dashboard
- [ ] Signal explorer
- [ ] Dataset provenance explorer
- [ ] Exportable intelligence reports

## What the new genomic layer does

BioSignal can now take a FASTA record:

`>contig-1`
`ACGT...`

and produce reproducible QC metadata:

- sequence length
- GC fraction
- ambiguous-base count
- N fraction
- QC status
- review warnings

The QC layer is deliberately lightweight and transparent.

BioSignal now also accepts standard four-line FASTQ records and converts Phred+33 quality characters into integer quality scores. The feature layer extracts transparent sequence-level statistics and configurable k-mer counts. K-mers containing ambiguous bases are skipped. These features are representations for downstream research; they do not by themselves identify genes or infer antimicrobial resistance. It is intended to identify records that require review before downstream analysis; it is **not** a clinical quality assessment and does not infer antimicrobial resistance.

## Genomic data sources

BioSignal uses NCBI Datasets as its genomic-data access layer. NCBI Datasets supports genome retrieval by taxonomy ID/name or accession and can provide sequence, annotation and sequence-report data.

The longer-term pathogen-genomics integration is NCBI Pathogen Detection, which documents workflows involving assembly, genomic clustering, SNP-based phylogenetic analysis and AMR gene/protein identification with AMRFinderPlus.

## Safety and governance

BioSignal is a research project, not a diagnostic or clinical decision-support system.

Do not commit names, contact details, medical record numbers, raw patient records, private laboratory records, credentials, or access tokens.

Use public, synthetic, or properly governed de-identified data. Genomic observations should remain traceable to their source accession and method.

Any clinical deployment would require appropriate validation, governance, security, and regulatory review.


## Annotation and AMR layer

BioSignal now parses NCBI-style GFF3 annotations into structured genome features and can normalize tabular AMRFinderPlus results into traceable AMR-hit records. NCBI provides GFF3 annotations with feature coordinates and attributes, while AMRFinderPlus uses curated reference genes and HMMs to identify AMR genes and resistance-associated point mutations. BioSignal treats those results as external evidence and preserves method/reference/coverage/identity metadata rather than implementing an unvalidated resistance classifier.

This phase does **not** claim that detection of an AMR-associated gene proves phenotypic resistance in an individual isolate. Genotype-to-phenotype linkage remains a separate research milestone.
