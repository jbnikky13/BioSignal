# BioSignal: independent scientific review brief

**Purpose:** Request critical scientific and technical feedback from antimicrobial-resistance (AMR), microbiology, epidemiology, bioinformatics, and surveillance researchers.

**Project:** BioSignal — https://github.com/jbnikky13/BioSignal  
**Review status:** Pre-publication, independent expert review requested  
**Development snapshot:** November 2026  
**Author:** Godam Sorbari Nichole, Independent Researcher and Developer, Port Harcourt, Nigeria  
**Contact:** godamsorbari13@gmail.com

## 1. What BioSignal is

BioSignal is an early-stage, open-source research and engineering framework intended to integrate structured AMR observations, pathogen metadata, genomic analysis outputs, and temporal/geographic summaries while retaining provenance and interpretation limits.

It is not a diagnostic, clinical decision-support, or operational public-health alerting system. Its current value proposition is an evidence-aware integration and reporting layer—not a new resistance assay, a replacement for WHO GLASS or AMRFinderPlus, or a validated predictor of future resistance.

## 2. Architecture and evidence-handling approach

The implemented and developing workflow is:

`public/permitted data → ingestion → normalization → provenance → quality checks → taxonomy/isolate metadata → sequence processing → annotation → AMR evidence → evidence-aware linkage/reporting`

Key components include:

- **Aggregated AST observations:** CSV ingestion into a canonical observation schema; source-specific normalization; retention of organism, antimicrobial, region, source, specimen and available testing metadata.
- **Provenance and comparability:** source information and dataset metadata are retained; observable differences or missing metadata can trigger caveats. Missing fields remain unknown. A `no_known_mismatch` status means only that no mismatch was detected in the available fields—it does not prove epidemiological equivalence.
- **Data-quality checks:** structural checks and minimum-sample safeguards are implemented. The quality score remains an uncalibrated engineering heuristic, not a probability, confidence score, or validated quality measure.
- **Public pathogen/genome metadata:** NCBI BioSample and assembly resolution, genome-package retrieval, and isolate identifiers support public-isolate workflows.
- **Sequence and annotation handling:** FASTA/FASTQ parsing, Phred+33 quality handling, feature extraction, and GFF3 parsing.
- **Genomic AMR evidence:** AMRFinderPlus results are normalized while retaining method, detection scope (including Core/Plus), locus/reference metadata, and software/catalog version information where available.
- **Workflow reproducibility:** Python tests, Nextflow orchestration, GitHub Actions validation, and a separately dispatched public-isolate workflow provide engineering checks and execution records.

### Interpretation safeguards

1. Phenotypic AST observations and genomic detections are distinct evidence types and are reported separately.
2. A detected gene or mutation is not, by itself, proof of phenotypic resistance.
3. Genotype–phenotype linkage requires verified matching isolate identifiers; aggregate observations must not be treated as isolate-level matches.
4. Core and Plus detections must remain distinguishable; review flags and uncertainty must not be silently discarded downstream.
5. Missing specimen, testing, laboratory, population, or provenance metadata are not inferred.
6. Signal/comparability labels are transparency aids, not calibrated confidence estimates or clinical recommendations.
7. Pharmacometric/PK-PD modelling is a possible future research direction only; no PK/PD model or dose recommendation is implemented.

## 3. Recovered WHO GLASS exploratory exercise

Two recovered dashboard exports match the filters, years, country counts, and row counts described in the development analysis. The author reports downloading them around the end of October 2026; the exact date, dashboard chart/export state, and source release/version are not embedded in the files. Their historical identity as the exact original downloads therefore remains unverified.

| Export | Coverage | Rows | Countries |
|---|---:|---:|---:|
| Bloodstream infection, *E. coli* / ceftriaxone | 2018–2023 | 114 country-years | 19 |
| Bloodstream infection, *Acinetobacter* spp. / colistin | 2018–2023 | 66 country-years | 11 |

Structural checks found no duplicate country-year keys or missing required parsed fields in the reviewed files. Reported resistance percentages were consistent, within rounding precision, with resistant counts divided by interpretable AST counts. These checks support internal consistency of the recovered exports; they do not establish surveillance representativeness, between-country comparability, or global population estimates.

A post-hoc next-year-change diagnostic was recomputed using an outcome defined as a resistance increase of at least five percentage points in the following year. Thresholds were selected after inspecting development data; the exercise is retrospective and exploratory.

| Dataset | Selected thresholds (current resistance; prior change) | Holdout TP / FP / TN / FN | Sensitivity | Specificity | PPV | Accuracy |
|---|---|---:|---:|---:|---:|---:|
| *E. coli* / ceftriaxone | 20%; 15 percentage points | 9 / 27 / 2 / 0 | 100% | 6.9% | 25% | 28.9% |
| *Acinetobacter* spp. / colistin | 30%; 15 percentage points | 0 / 2 / 16 / 4 | 0% | 88.9% | 0% | 72.7% |

The contrasting results and error burden do not support a claim of useful predictive performance. The small number of positive outcomes, repeated country observations, post-hoc outcome/threshold choices, and lack of cluster-aware uncertainty estimates make the metrics unstable and unsuitable as evidence of generalization.

The auxiliary testing-coverage export contains 104 rows across six pathogens and five antibiotic groups (2016–2023); it was not used in these two pathogen–antimicrobial analyses.

## 4. Main validation limitations

- **Source provenance:** approximate download timing is now author-reported as late October 2026, but exact retrieval date, chart/export view, source release/version, and historical identity remain unresolved.
- **Data rights:** redistribution terms for the source exports have not yet been confirmed; raw CSVs are therefore not included in the public repository.
- **Representativeness:** aggregate country-year data are subject to surveillance participation, testing coverage, case mix, laboratory practice, and reporting differences. The pooled calculations are not global population estimates.
- **Exploratory diagnostic design:** outcome and thresholds were post-hoc; small holdout event counts and repeated observations weaken independence and stability.
- **Uncertainty:** no cluster-aware confidence intervals or robust country-level resampling have been reported.
- **External validation:** no independent dataset or prospective surveillance period has validated the signal rules.
- **Comparative evaluation:** no head-to-head functional, usability, or performance comparison with related tools has been completed.
- **Genomic linkage:** isolate-level concordance and causal genotype–phenotype interpretation require verified paired data and pinned tool/reference versions.
- **Software maturity:** BioSignal remains an early prototype; a final release, DOI archive, and release-level reproducibility audit are not complete.

## 5. Questions for independent experts

We would particularly value written comments on the following:

1. **Scientific framing:** Is the distinction between aggregated phenotypic surveillance, isolate-level AST, and genomic marker detection sufficiently explicit? Where could readers still overinterpret the outputs?
2. **Canonical data model:** Are the observation fields and provenance metadata adequate for cross-source AMR analysis? Which additional variables are essential for assessing comparability?
3. **Quality and comparability:** Are the current checks and minimum-sample safeguards defensible? What should replace or supplement the uncalibrated quality heuristic?
4. **WHO GLASS analysis:** Are the denominators, pooling approach, country-year unit, and limitations described appropriately? What additional coverage or stratification analyses are necessary?
5. **Diagnostic evaluation:** Is the next-year-change question scientifically useful? How would you redesign it—pre-specified outcome, country-level temporal split, clustered resampling, calibration, baseline comparison, and/or external validation?
6. **Genomic evidence:** Are Core/Plus scope, method/catalog provenance, review flags, and genotype–phenotype boundaries represented appropriately? What evidence is required before linkage claims are made?
7. **Benchmarking:** Which existing tools or workflows are the most relevant comparators, and what fair functional comparison would demonstrate a meaningful contribution?
8. **Governance and reproducibility:** What data licensing, metadata, software pinning, test fixtures, and archival practices should be mandatory before public release?

Please distinguish critical blockers from improvements that can reasonably follow in later development.

## 6. Potential collaboration

We are seeking a small number of AMR researchers and technical collaborators to help with:

- scientific review of the observation schema, evidence model, and report language;
- independent reproduction of the WHO GLASS descriptive analysis;
- redesign of the exploratory temporal evaluation with a pre-specified protocol and appropriate country-level validation;
- review of genomic evidence harmonization and isolate-level linkage requirements;
- selection of comparable tools and a fair functional evaluation;
- advice on data governance, release reproducibility, and a future validation dataset.

Possible collaboration can begin with a focused review of this brief and repository, followed—if there is mutual interest—by a short technical meeting or a jointly designed validation workstream. No institutional endorsement, data access, or clinical deployment is assumed.

## 7. Materials and requested response

Repository and current development branch: https://github.com/jbnikky13/BioSignal  
Open validation-readiness PR: https://github.com/jbnikky13/BioSignal/pull/7  
WHO GLASS source manifest: `data/examples/who-glass-source-manifest.csv`  
Manuscript draft: `paper/manuscript.md`  
Source recovery and reproducibility notes: `paper/WHO_GLASS_DATA_RECOVERY.md`

**Requested response:** A brief assessment of (a) the most important scientific or methodological concern, (b) the minimum changes required before independent reproduction, and (c) whether you would be interested in a follow-up discussion or collaboration.

We welcome critical feedback. The purpose of this review is to identify weaknesses and improve the scientific validity of BioSignal before making publication or performance claims.
