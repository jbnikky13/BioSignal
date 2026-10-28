# Pre-specified country-held-out evaluation protocol

**Status: NOT YET EXPERT-APPROVED. Do not run on real outcomes yet.**

The WHO GLASS dashboard exports contain country-year resistance proportions, not independently adjudicated alert outcomes or expert data-quality labels. The earlier next-year increase of at least 5 percentage points was selected post hoc and must not be treated as a pre-registered or clinically justified outcome.

## Required decisions before analysis

An AMR epidemiologist or surveillance expert must approve and document:

1. Intended use, analysis unit, outcome definition, forecast horizon, inclusion/exclusion rules, missingness handling, and clinical/operational rationale.
2. Independent outcome source and adjudication method. Never derive the reference label from BioSignal's own alert.
3. Expert role, approval date, and traceable approval reference.
4. Countries selected for holdout before their outcome labels are inspected or thresholds tuned. Document deployment relevance.
5. Frozen BioSignal thresholds, minimum-sample safeguard, and baseline thresholds.
6. Metrics and acceptable trade-offs. Report confusion counts, denominators, sensitivity, specificity, PPV, NPV and false-positive rate; do not select by accuracy alone.
7. Country-cluster uncertainty method. Multiple years within a held-out country remain correlated; this script reports per-country breakdowns but does not calculate cluster-aware intervals.
8. Four same-row comparators: always-negative, current-rate-only, change-only, and the combined BioSignal rule.
9. Separate blinded expert labels for data-quality-score evaluation. AMR event outcomes cannot calibrate the data-quality score.

## Input and execution

Use data/examples/calibration_template.csv as the labelled-record schema. Every row must contain a real independent binary reference outcome, source/protocol provenance, country identifier in surveillance_unit, dataset release, coverage notes, rates, sample counts, and period. Synthetic test fixtures are software tests only.

The CLI requires a JSON protocol with protocol_id, outcome_definition, expert_approval (status approved, expert_role, approval_date, approval_reference), protocol_frozen_before_holdout_review=true, holdout_countries, thresholds (alert_rate, alert_change_percentage_points, minimum_samples), and baseline_thresholds (current_rate, change_percentage_points). All placeholders and illustrative values must be replaced with expert-approved choices. The script rejects pending approval, protocol ID mismatches, absent holdout countries, and empty partitions. It does not tune thresholds.

After approval, run:
python scripts/evaluate_country_holdout.py labelled_outcomes.csv --protocol approved_protocol.json

## Release gate

This is evaluation infrastructure, not validation evidence. Do not claim clinical validity without adequate independent labels, coverage/representativeness review, cluster-aware uncertainty, external expert review, and a documented release decision. Keep data_quality_score labelled uncalibrated_heuristic until blinded independent expert-quality labels exist.
