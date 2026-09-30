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
- [x] Isolate-level identifiers and matching
- [x] AMR evidence harmonization
- [x] Reproducible Nextflow workflow skeleton
- [x] Real public NCBI BioSample integration test (opt-in)
- [x] First end-to-end public-isolate evidence report
- [x] NCBI BioSample → assembly resolution layer
- [x] End-to-end genome download → AMRFinderPlus execution workflow
- [x] GitHub Actions runner for reproducible public-isolate experiments
- [x] Lightweight CI compile/test gate for the Nextflow workflow
- [x] Scheduled public integration workflow

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


## Workflow milestone

BioSignal now has canonical isolate identity fields (BioSample, assembly and SRA accessions) and AMR evidence harmonization that preserves AMRFinderPlus method, identity, coverage, software version and reference-catalog version. A Nextflow workflow skeleton provides a reproducible execution boundary for FASTA → AMRFinderPlus analysis. Production runs should pin tool/database versions and validate against a public dataset before interpretation.


## First public integration dataset

BioSignal now includes an opt-in live NCBI BioSample integration test using SAMN05170351. NCBI documents this public Escherichia coli isolate as part of PRJNA288601, with sequencing data and an antibiogram. The integration client retrieves the public BioSample record through NCBI E-utilities and normalizes core isolate metadata.

Run the live check with:

    BIOSIGNAL_LIVE_NCBI=1 pytest -m integration

The repository also keeps a small metadata-only fixture under data/public/ so the expected public record is reviewable without requiring a network call.

The integration layer deliberately stops at public metadata. It does not download patient records, private clinical data, or large genome collections.


## First end-to-end experiment

BioSignal now has a reproducible evidence-report layer for public isolate SAMN05170351. The report connects public BioSample metadata, genomic AMR evidence and submitted AST phenotype as separate evidence streams.

The report intentionally does not claim genotype-phenotype causality. Isolate-level concordance requires verified matching identifiers and pinned genomic-analysis versions.

See `reports/SAMN05170351.md`.


### Assembly-resolution milestone

BioSignal can now resolve public genome assemblies from a BioSample accession through the NCBI Datasets v2 genome/BioSample endpoint. This closes the metadata-to-genome handoff without hard-coding an assembly accession.

The public integration workflow is scheduled weekly and can also be dispatched manually. It runs the opt-in NCBI integration test against live public data.

NCBI documents BioSample, Assembly, AST phenotype and AMRFinderPlus genotype as linked fields in its Pathogen Detection ecosystem. The Datasets API also supports genome metadata lookup by BioSample accession. citeturn2search3turn0search1


## End-to-end public isolate execution

BioSignal now includes `workflows/public_isolate.nf`, which connects the real execution stages:

1. Resolve a BioSample to an NCBI assembly.
2. Download the genome and GFF3 package from NCBI Datasets.
3. Locate the genomic FASTA.
4. Run AMRFinderPlus.
5. Capture the AMRFinderPlus version.
6. Publish the experiment outputs as a GitHub Actions artifact.

The workflow is exposed through `.github/workflows/public-isolate-experiment.yml` and can be manually dispatched with a BioSample accession. NCBI Datasets packages can contain genome sequences, GFF3 annotation and metadata, and NCBI documents assembly accessions as versioned identifiers for reproducibility. citeturn0search4turn0search10

The workflow does not claim an analysis result until the run actually completes. This keeps the repository's scientific status separate from its pipeline definition.


### Pipeline reliability hardening

The public-isolate pipeline now has a separate lightweight validation workflow. Every relevant push/PR can compile the Nextflow workflow in stub mode and run the Python test suite before the live NCBI/AMRFinderPlus experiment is manually dispatched.

The live experiment is hardened to:

- pin AMRFinderPlus software to 4.2.7;
- initialize and report the AMRFinderPlus database version;
- retrieve both genomic FASTA and GFF3 from the NCBI genome package;
- run AMRFinderPlus with nucleotide + GFF evidence and an *Escherichia* organism scope;
- fail if the expected FASTA, GFF or AMRFinder output is missing;
- publish the assembly manifest, AMRFinder output, tool-version record and Nextflow execution reports as artifacts.

NCBI documents that AMRFinderPlus accepts assembled nucleotide sequence and can use GFF annotation, and NCBI's own CI examples exercise combined nucleotide/protein/GFF modes with organism-specific mutation screening. citeturn0search0turn4search0
