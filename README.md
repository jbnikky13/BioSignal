# BioSignal

**Biological health intelligence for pathogen surveillance and antimicrobial-resistance signals.**

BioSignal is an open-source research and engineering project for turning fragmented, aggregated biological and clinical observations into explainable signals about pathogens, antimicrobial resistance (AMR), treatment patterns, and temporal/geographic trends.

> **Core principle:** intelligence, not identities.

## Current pipeline

Public / permitted data  
→ ingestion  
→ normalization  
→ provenance  
→ data-quality assessment  
→ explainable AMR signal

The project currently includes a WHO GLASS-AMR source adapter and a transparent data-quality layer. WHO GLASS emphasizes improving AMR data quality, completeness and representativeness, and documents limitations such as selective testing, sampling bias and diagnostic constraints. BioSignal therefore treats data quality as part of the signal itself rather than an afterthought.

## Data-quality model

BioSignal evaluates three transparent dimensions:

- sample sufficiency
- metadata completeness
- observation-window coverage

These are engineering heuristics for research prioritization, not clinical or epidemiological confidence intervals.

## Roadmap

### Phase 1 — Foundation
- [x] Repository architecture
- [x] Canonical observation schema
- [x] Deterministic resistance signal engine
- [x] Unit tests
- [x] Public dataset source definition

### Phase 2 — Data engineering
- [x] CSV ingestion
- [x] WHO GLASS-AMR query builder
- [x] Runtime public-data fetcher
- [x] Dataset provenance
- [x] Data-quality assessment
- [ ] Real-data normalization adapter
- [ ] Reproducible ingestion command

### Phase 3 — Bioinformatics
- [ ] Pathogen taxonomy normalization
- [ ] FASTA/FASTQ support
- [ ] Sequence QC metadata
- [ ] Genomic annotation
- [ ] Reproducible Nextflow/Snakemake workflow

### Phase 4 — Intelligence
- [ ] Temporal anomaly detection
- [ ] Geographic aggregation
- [ ] AMR trend analysis
- [ ] Molecular resistance markers
- [ ] Signal calibration against published surveillance metrics

### Phase 5 — Interface
- [ ] Research dashboard
- [ ] Signal explorer
- [ ] Dataset provenance view
- [ ] Exportable intelligence reports

## Safety and governance

BioSignal is a research project, not a diagnostic or clinical decision-support system.

Do not commit names, contact details, medical record numbers, raw patient records, private laboratory records, credentials, or access tokens.

Use public, synthetic, or properly governed de-identified data. Any clinical deployment would require appropriate validation, governance, security, and regulatory review.


### Genomic integration

BioSignal now includes an NCBI Datasets layer for bounded genome metadata queries and reproducible genome-package command construction. NCBI supports genome retrieval by taxon or accession and can include sequence, annotation and sequence-report files. The next milestone is a small reproducible bacterial dataset, followed by sequence QC and AMR annotation.

NCBI Pathogen Detection is the longer-term bridge to pathogen genomics and AMR: its documented workflow includes assembly, genomic clustering, SNP-based phylogenetic analysis and AMR gene/protein identification using AMRFinderPlus.
