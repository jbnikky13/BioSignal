# WHO GLASS exploratory evaluation protocol

**Status: protocol proposal for review; not a confirmatory or clinical validation protocol.** The current two exports have already been inspected, so this document cannot make the present analysis pre-registered. Any confirmatory evaluation must use a newly frozen protocol and untouched data or an independent cohort.

## Data and import

The current public dashboard exports cover bloodstream infection:

- *Escherichia coli* / ceftriaxone, 2018–2023.
- *Acinetobacter* spp. / colistin, 2018–2023.

The WHO dashboard CSV contains both chart-level distribution summaries and a country-level table under `Data for line plots for individual CTAs`. Analyses must use the country-level table, not the Min/Q1/Median/Q3/Max summary as if those quantiles were observations.

Run the structural audit:

```bash
python scripts/audit_who_glass_export.py "Time series of resistance to antibiotics (2018-2023)_All-BLOOD 2.csv" --normalized-csv /tmp/ecoli-ceftriaxone.csv
python scripts/audit_who_glass_export.py "Time series of resistance to antibiotics (2018-2023)_All-BLOOD.csv" --normalized-csv /tmp/acinetobacter-colistin.csv
```

Preserve the original CSV unchanged and record the dashboard URL, retrieval date, filters, file checksum, and any release/version identifier that WHO provides. If a release/version is not available in the export, record it as unavailable rather than guessing. Do not commit raw data exports unless repository licensing and governance have been reviewed.

## Integrity checks

The importer validates required columns, numeric fields, positive interpretable AST denominators, resistant counts no greater than interpretable AST, interpretable AST no greater than total specimen isolates, percentages against counts within rounding tolerance, and duplicate country-year keys. It reports whether the included countries form a balanced panel. Passing these checks demonstrates structural consistency only.

## Estimands and outcomes

Do not call a pooled sum(resistant)/sum(interpretable AST) rate a global estimate. It weights reporting countries by their AST denominators and can be dominated by large contributors. Report it only as a descriptive pooled rate among the countries present. Also report country-level distributions, denominators, missingness, and coverage context.

A candidate retrospective forecast estimand is whether the same country's reported resistance proportion rises by a prespecified amount in the next year. Before a confirmatory evaluation, an AMR domain expert must define and justify:
- the exact change threshold and whether the outcome is absolute percentage points or relative change;
- minimum denominators and any uncertainty-aware outcome rule;
- how to handle small AST denominators, zero counts, missing years, and changes in laboratory standards;
- the intended use and costs of false alerts versus missed events.

The previously explored +5 percentage-point outcome was chosen after inspecting the data. It is post-hoc exploratory and must not be presented as a clinically meaningful threshold or as pre-registered.

## Split design

A single six-year dashboard export is too small for strong temporal and external validation. For a new confirmatory cohort:

1. Freeze the dataset release and analysis protocol before fitting thresholds.
2. Hold out entire countries, not random rows, for the primary transportability assessment. Select the held-out countries in advance and justify coverage/region balance. Never let a country's years appear in both development and external test sets.
3. Within development countries, use a chronological split for threshold selection. Freeze the threshold and every preprocessing choice before evaluating the held-out countries.
4. If temporal performance is also claimed, use a later period from countries not used for threshold tuning or clearly label the evaluation as temporal-but-not-external. Do not reuse the same holdout to select an operating point.
5. Repeat only as a separately labelled sensitivity analysis, not to choose whichever split looks best.

The existing 2018–2023 data have repeated countries over time and few years. Any exploratory split on these exports has small effective sample size and must disclose that limitation.

## Metrics and uncertainty

Report confusion-matrix counts and denominators, sensitivity, specificity, PPV, NPV, false-alert rate, missed-event rate, and prevalence. Include uncertainty intervals. Because observations are clustered by country, row-wise binomial intervals are insufficient for generalization; use a country-cluster bootstrap or another design-appropriate method once the number of independent countries is sufficient. Show country-level results and subgroup failures, not just pooled metrics.

Compare against prespecified baselines, including:
- always-no-alert;
- persistence/no-change forecast;
- a simple previous-rate or previous-change rule;
- the existing BioSignal threshold rule.

Do not optimize against the held-out cohort. Do not report accuracy alone for rare outcomes. If sample size or positive event counts are too small, state that estimates are unstable and stop short of a performance claim.

## Quality-score evaluation is a separate study

These resistance exports contain no independent quality labels. They cannot calibrate `data_quality_score`. A separate study needs blinded expert assessments using a documented rubric covering denominator integrity, surveillance coverage, representativeness, deduplication, metadata completeness and testing comparability. Develop any cutoff on one set and assess it on a disjoint external set. AUROC assesses ranking discrimination only; probability calibration requires a score intended as a probability and an untouched calibration evaluation.

## Release gate

Do not describe BioSignal as scientifically calibrated, clinically validated, or representative based on these exports. Release claims require independent review of the protocol, dataset provenance, coverage, laboratory comparability, uncertainty method, subgroup performance and intended-use risks. This work is research only and must not drive treatment or public-health decisions.
