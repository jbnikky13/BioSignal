# BioSignal 0.1.0 — release candidate

**Status:** preparation branch only; not a published release or DOI-backed archive.

## Included

- AMR observation ingestion, normalization, and provenance.
- WHO GLASS dashboard-export structural audit and descriptive summary utilities.
- Public NCBI BioSample/assembly resolution and public-isolate workflow.
- FASTA/FASTQ processing and GFF3 parsing.
- AMRFinderPlus evidence harmonization and evidence-aware JSON/Markdown reports.
- Scientific validation plan, empty validation intake template, expert feedback pathway, and descriptive WHO-region/year summaries.
- Reproducibility protocol and source-data manifest template.
- Software citation metadata and Apache-2.0 licensing files.

## Important limitations

- No independent, expert-labelled validation cohort has been evaluated.
- The initial WHO GLASS exports are not yet archived with source filters, retrieval dates, and checksums.
- The exploratory next-year diagnostic is post-hoc and must not be described as confirmatory validation.
- The public-isolate workflow and stub-mode CI checks do not establish biological, clinical, or epidemiological validity.
- No pharmacometric PK/PD modelling is implemented in this version.

## Release gate

Do not tag or archive this version until the clean-install test suite, Nextflow stub workflow, exact source-data provenance, licence consistency, and public-isolate run are checked against the final release commit. Archive the exact tagged source in Zenodo and add the resulting DOI to the citation metadata and manuscript.
