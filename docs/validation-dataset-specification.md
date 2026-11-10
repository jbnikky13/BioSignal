# AMR validation dataset specification

**Status:** intake specification; no independent validation cohort is currently certified by this document.

## 1. Purpose and separation of datasets

BioSignal must maintain three distinct data classes:
1. **Software test fixtures:** small synthetic records used only to test parsing, validation, and metrics. Never use these to claim scientific performance.
2. **Exploratory public surveillance data:** public aggregate records used for descriptive analysis and hypothesis generation. These do not automatically provide independent alert labels.
3. **Evaluation cohort:** governed, provenance-complete records with independently defined outcomes and a frozen protocol. Only this cohort can support a validation claim, subject to design and expert review.

Never mix these classes in one metric table without explicit labels.

## 2. Required record fields

The canonical evaluation template is data/examples/validation_dataset_template.csv.

Each record should identify:
- observation period and stable organism, antimicrobial, specimen, source, laboratory method, testing criteria, region, and surveillance unit;
- tested/interpretable and resistant counts, with a documented denominator definition;
- dataset release, retrieval date, source URL/reference, coverage notes, and raw-file checksum where permitted;
- independent binary reference outcome, its source, adjudication method, and protocol ID;
- whether the record is eligible for development or holdout, assigned before inspecting holdout outcomes.

Use explicit values such as unknown or not_reported for unavailable metadata. Do not infer missing fields.

## 3. Reference outcome rules

A reference outcome must be defined independently of BioSignal's threshold or alert output. Examples for expert discussion include a pre-specified, independently adjudicated surveillance event or a future-period outcome defined before model development. The outcome must have a scientific or operational rationale and a fixed horizon.

The earlier exploratory +5 percentage-point next-year increase is post-hoc and must not be reused as a confirmatory endpoint without a new expert-approved rationale and untouched cohort.

## 4. Source intake checklist

For each dataset release, retain the original download unchanged (outside the public repository if licensing or governance requires), source name and URL, retrieval timestamp, release/version, selected filters and query, license/terms, file checksum (SHA-256), row counts before and after filtering, inclusion/exclusion and deduplication rules, country/site and time coverage, missingness, denominator definitions, known laboratory standard/method changes, and transformation script/version.

## 5. Split and evaluation design

Prefer a preselected external-country/site holdout for transportability and a separate chronological evaluation for temporal performance. Do not allow the same country/site to contribute to both development and external holdout. Thresholds and preprocessing must be selected on development data only and frozen before holdout evaluation.

Report the full confusion matrix, sensitivity, specificity, PPV, NPV, false-positive rate, missed-event rate, prevalence, and denominators. Use cluster-aware uncertainty when repeated records are nested within countries/sites. Compare with pre-specified simple baselines. Report subgroup failures and abstain from performance claims when independent units or positive outcomes are too few.

## 6. Data-quality labels are a separate study

AMR event outcomes cannot calibrate the data-quality heuristic. A separate blinded expert review must label data quality using a written rubric covering denominator validity, coverage, representativeness, deduplication, metadata completeness, and testing comparability. Evaluate on a disjoint holdout.

## 7. Release gate

A dataset is not an evaluation cohort until source provenance, governance, coverage, independent labels, protocol freeze, and holdout assignment have been reviewed. The presence of a populated CSV is not evidence of validation. Do not publish identifiable or restricted data.
