# BioSignal

**Biological health intelligence for pathogen surveillance and antimicrobial-resistance signals.**

BioSignal is an open-source research and engineering project for turning aggregated biological and clinical observations into explainable signals about pathogens, antimicrobial resistance (AMR), and temporal/geographic trends.

> **Core principle:** intelligence, not identities.

## Current status

**Phase 3 — Bioinformatics: IN PROGRESS**

Phases 1 and 2 are complete. Phase 3 now covers sequence handling, genome annotation, structured AMR evidence, and an evidence-aware genotype/phenotype linkage layer.

## Pipeline

Public / permitted data  
→ ingestion  
→ normalization  
→ provenance  
→ quality assessment  
→ pathogen taxonomy  
→ genomic metadata  
→ FASTA/FASTQ  
→ sequence QC/features  
→ GFF3 annotations  
→ AMR evidence  
→ genotype/phenotype linkage  
→ intelligence

## Phase 1 — Foundation — COMPLETE
- [x] Repository architecture
- [x] Canonical AMR observation schema
- [x] Deterministic resistance signal engine
- [x] Unit tests
- [x] Public source definitions

## Phase 2 — Data Engineering — CORE COMPLETE
- [x] CSV ingestion
- [x] WHO GLASS-AMR query builder
- [x] Runtime public-data fetcher
- [x] Dataset provenance
- [x] Data-quality assessment
- [x] Explicit source-to-canonical normalization

## Phase 3 — Bioinformatics — IN PROGRESS
- [x] NCBI Taxonomy normalization
- [x] NCBI genomic metadata/query layer
- [x] FASTA parser
- [x] FASTA QC
- [x] FASTQ parser
- [x] Phred+33 quality parsing
- [x] Sequence feature extraction
- [x] GFF3 annotation parsing
- [x] AMR result ingestion
- [x] Evidence-aware genotype/phenotype linkage
- [ ] Isolate-level identifiers and matching
- [ ] AMR evidence harmonization
- [ ] Reproducible Nextflow/Snakemake workflow
- [ ] Real public dataset integration test

## Phase 4 — Intelligence — NOT STARTED
- [ ] Temporal anomaly detection
- [ ] Geographic aggregation
- [ ] AMR trend analysis
- [ ] Genomic resistance-marker analysis
- [ ] Genotype/phenotype relationship analysis
- [ ] Signal calibration against published surveillance metrics

## Phase 5 — Interface — NOT STARTED
- [ ] Research dashboard
- [ ] Signal explorer
- [ ] Dataset provenance explorer
- [ ] Exportable intelligence reports

## Genotype/phenotype boundary

WHO GLASS surveillance includes phenotypic resistance measurements, while NCBI AMRFinderPlus identifies AMR genes and resistance-associated point mutations using curated references and HMMs. These are complementary evidence types, not interchangeable measurements.

BioSignal therefore reports genomic evidence separately from phenotype. A detected AMR gene or mutation does **not** automatically prove phenotypic resistance, particularly when genomic and phenotype observations are not from the same isolate. The linkage layer preserves this limitation explicitly.

## Governance

BioSignal is a research project, not a diagnostic or clinical decision-support system.

Do not commit names, contact details, medical record numbers, raw patient records, private laboratory records, credentials, or access tokens.

Use public, synthetic, or properly governed de-identified data. Any clinical deployment would require appropriate validation, governance, security, and regulatory review.
