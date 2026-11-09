# BioSignal: An African-led, evidence-aware AMR surveillance research platform

**Technical concept note for scientific collaboration**  
**Prepared:** 9 November 2026  
**Project stage:** Early research and engineering prototype  
**Lead:** Jbnikky13 (independent project; collaborators and institutional affiliations to be confirmed)

## 1. Overview and rationale

Antimicrobial resistance (AMR) surveillance depends on data that are sufficiently complete, comparable, and interpretable across laboratories, locations, organisms, antimicrobials, and time. In many low- and middle-income settings, surveillance data may be fragmented across laboratory systems, public datasets, and research outputs. Differences in sampling, testing standards, denominators, reporting coverage, and genomic methods can make comparisons difficult.

BioSignal is an open-source research prototype exploring how public and appropriately governed biological and surveillance data can be transformed into transparent, reproducible AMR evidence summaries. The project is being developed with an African-led perspective and an initial focus on methods that could support research and surveillance capacity in African and other resource-constrained settings.

BioSignal is not a diagnostic tool, clinical decision-support system, or validated public-health alerting service. Its present purpose is to establish reproducible data engineering, genomic evidence handling, and evaluation methods that can be reviewed and improved with AMR epidemiologists, microbiologists, bioinformaticians, and surveillance practitioners.

## 2. Objectives

The proposed collaboration would help BioSignal:
1. Improve the quality, traceability, and interoperability of public AMR surveillance and pathogen-genomics data.
2. Preserve the distinction between phenotypic antimicrobial susceptibility testing (AST) observations and genomic detections.
3. Develop transparent geographical and temporal summaries that expose denominators, country coverage, and comparability limitations.
4. Evaluate candidate trend signals against independently defined reference outcomes using pre-specified, leakage-aware methods.
5. Establish a pathway for expert review, validation, and responsible future development.

## 3. Technical architecture and current development

The current Python and Nextflow architecture follows a modular pipeline:

**Permitted data sources → ingestion → normalization → provenance → data-quality checks → taxonomy and isolate metadata → sequence processing → AMR evidence → evidence-aware reporting → aggregate surveillance summaries.**

Implemented capabilities include:
- CSV ingestion and canonical AMR observation models.
- WHO GLASS dashboard export parsing, extracting country-level rows rather than chart quantiles.
- Integrity checks for AST denominators, resistant counts, reported percentages, duplicate country-year records, and selected dashboard filters.
- Dataset provenance and explicit source-to-canonical normalization.
- NCBI BioSample and assembly metadata resolution.
- FASTA/FASTQ parsing and sequence-quality features.
- GFF3 annotation parsing and AMRFinderPlus evidence ingestion.
- Preservation of AMRFinderPlus Core/Plus scope, detection type, method, identity, reference coverage, genomic location, and manual-review flags.
- Unified JSON and Markdown isolate reports with downstream consistency checks.
- A validation harness supporting chronological and external surveillance-unit holdouts, threshold freezing, and standard binary classification metrics.

A public-isolate workflow has been exercised through GitHub Actions. The repository contains an example public BioSample analysis and records the distinction between software workflow validation and biological interpretation. A successful workflow run does not establish clinical or epidemiological validity.

## 4. Data sources and governance

The initial data-source strategy uses public, documented sources, including:
- **WHO GLASS-AMR:** aggregate national surveillance observations and dashboard exports, subject to release, filter, denominator, and coverage review.
- **NCBI BioSample, Assembly, and Pathogen Detection resources:** public isolate and genome metadata where access and reuse terms permit.
- **NCBI AMRFinderPlus:** curated genomic detection outputs, with software and reference-database versions recorded.
- **Other public surveillance datasets:** considered only after source documentation, licensing, inclusion criteria, laboratory comparability, and coverage have been reviewed.

No patient-level or restricted laboratory data are required for the current prototype. Any future access to non-public or identifiable data would require an appropriate data-sharing agreement, ethics and governance review, security controls, and documented permitted use. Raw source exports should be retained with retrieval date, filters, release/version where available, checksum, and transformation history. Missing source metadata must be recorded as unknown rather than inferred.

## 5. Scientific safeguards and validation approach

BioSignal deliberately keeps genomic and phenotypic evidence separate. Detection of an AMR-associated gene or mutation is not, by itself, confirmation of phenotypic resistance, expression, or treatment response. Genotype–phenotype linkage is only considered when isolate identifiers and evidence streams can be verified as belonging to the same isolate.

Current aggregate trend thresholds and the data-quality score are uncalibrated engineering/research heuristics. Wilson intervals describe binomial uncertainty for individual proportions only; they do not correct for sampling bias, clustering, repeated isolates, non-independent observations, or representativeness.

A credible validation programme should be co-designed with domain experts and include:
1. A pre-specified intended use, unit of analysis, outcome definition, forecast horizon, and inclusion/exclusion criteria.
2. An independent reference outcome that is not derived from BioSignal's own alert rule.
3. Dataset release, provenance, denominator, deduplication, laboratory-method, and geographic-coverage documentation.
4. Development data separated from untouched temporal and/or external country/site holdouts.
5. Threshold selection on development data only, with frozen thresholds evaluated once on holdout data.
6. Sensitivity, specificity, positive and negative predictive values, false-positive and missed-event counts, denominators, uncertainty, subgroup performance, and baseline comparisons.
7. Independent expert review of discordant cases and a separate blinded assessment of data quality if the data-quality heuristic is to be evaluated.

An initial WHO GLASS exploratory exercise has been documented for E. coli/ceftriaxone and Acinetobacter spp./colistin bloodstream exports from 2018–2023. It is explicitly post-hoc and descriptive/diagnostic, not confirmatory validation. The observed false alarms and missed events reinforce the need for expert-defined outcomes and independent country-level evaluation.

## 6. Proposed collaboration and expert input

We would welcome AMRIF's guidance on the scientific scope and a practical route to expert feedback. Priority areas for collaboration are:
- Review of the data model and interpretation boundaries between AST and genomic evidence.
- Advice on suitable public or governed datasets, organism–antimicrobial combinations, and surveillance units.
- Co-definition of a defensible reference outcome and validation protocol.
- Review of denominator handling, laboratory comparability, deduplication, and country/site holdout design.
- Feedback on geographical and temporal summaries and the limitations that should accompany them.
- Identification of potential microbiology, epidemiology, bioinformatics, and public-health collaborators.

A proposed first step is a technical review meeting or written review of the repository's validation protocol and a small reproducible example. A second step could be a jointly scoped pilot using an approved dataset and pre-agreed evaluation protocol. Any expanded access to data or operational use would be subject to relevant institutional approvals and governance.

## 7. Development status and next milestones

| Workstream | Current position | Next milestone |
|---|---|---|
| Core data and provenance | Implemented prototype | Expert review of canonical fields and provenance |
| Genomic evidence | AMRFinderPlus integration and unified reports implemented | Review against curated reference isolates and AST where matched |
| Validation | Evaluation utilities and exploratory WHO GLASS pilot documented | Expert-approved outcome and independent country/site holdout |
| Geography and time | Country-year parsing and descriptive summaries implemented | WHO-region/year summaries with coverage and denominator reporting |
| Interface | Not yet built | Dashboard only after data model and summaries are reviewed |

## 8. Limitations and intended use

BioSignal is an early-stage research and engineering prototype. Available public examples and exploratory aggregate exports do not establish representativeness, external validity, clinical validity, or readiness for routine surveillance decisions. Some public isolate analyses may use a reference database that changes over time; exact software and database versions must be retained, and database pinning remains a reproducibility consideration.

The project will not recommend treatment, infer patient-level resistance from aggregate data, or issue operational public-health alerts. Any future decision-support or deployment proposal would require independent validation, expert governance, security, ethics, and regulatory review appropriate to its intended use.

## 9. References and project materials

- BioSignal repository: https://github.com/jbnikky13/BioSignal
- WHO GLASS-AMR: https://www.who.int/initiatives/glass/glass-routine-data-surveillance
- WHO GLASS AMR dashboard: https://data.who.int/dashboards/amr/overview
- NCBI AMRFinderPlus: https://www.ncbi.nlm.nih.gov/pathogens/antimicrobial-resistance/AMRFinder/
- NCBI Datasets: https://www.ncbi.nlm.nih.gov/datasets/
- Scientific validation plan: scientific-validation-plan.md
- WHO GLASS protocol: who-glass-validation-protocol.md
- Country-held-out protocol: country-held-out-evaluation-protocol.md
