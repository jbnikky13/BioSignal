# Scientific validation plan

## Current status

BioSignal's aggregated AMR trend thresholds and data-quality score are research heuristics. They have **not** been calibrated against surveillance outcomes or validated as epidemiological cutoffs. The Wilson intervals currently emitted for resistance proportions quantify binomial sampling uncertainty only; they do not address selection bias, clustering, duplicate isolates, non-independent observations, or representativeness.

No result from synthetic unit tests should be described as scientific validation.

## Data required before calibration

Calibration must not be claimed until a governed, representative, sufficiently documented surveillance dataset is available with, at minimum:

- stable organism, antimicrobial, region, period, specimen, source/laboratory, testing standard and method identifiers;
- tested and resistant counts, plus denominators and missingness rules;
- a pre-defined independent reference outcome for each alert (for example, an adjudicated surveillance signal or a pre-specified later-period outcome);
- documentation of sampling design, deduplication, patient/isolate inclusion criteria, and major changes in laboratory practice;
- enough independent sites, regions and time periods to support separated development and evaluation sets.

Do not infer an independent reference outcome from BioSignal's own threshold output. That would be circular validation.

## Required evaluation protocol

1. Pre-register the target use, unit of analysis, reference outcome, inclusion/exclusion criteria, metrics, acceptable error rates and intended operating point.
2. Keep related observations from the same site/region and overlapping periods in the same split where feasible. Prefer a chronological holdout and, where data allow, an external site/region holdout to reduce leakage.
3. Tune thresholds only on the development set. Freeze the thresholds before evaluating the holdout set.
4. Report sensitivity, specificity, positive predictive value, negative predictive value, false-alert rate, missed-event rate, calibration where a probability is actually produced, and uncertainty intervals. Report denominators and missingness for every metric.
5. Compare against simple pre-specified baselines and repeat across organisms, antimicrobials, regions, laboratories and time periods. Investigate subgroup failures and dataset shifts.
6. Have domain experts review discrepancies and determine whether the reference labels and surveillance design support the intended interpretation.
7. Publish the dataset provenance, protocol, code/version, threshold selection, holdout results and limitations. If data are not shareable, publish a reproducible summary sufficient for independent review.

## Comparability is not proven by matching metadata

Matching region, source, specimen type, testing criteria and laboratory method only means no mismatch was detected in those fields. It does not establish comparable patient mix, testing indications, deduplication, healthcare setting, laboratory implementation, access to testing, or reporting coverage. Those factors should be added to the data model when reliably available and assessed by domain experts. Missing information must remain unknown, not be imputed as equivalence.

## Uncertainty limits

The Wilson 95% intervals are descriptive binomial intervals for each proportion. They are not intervals for the between-period difference and do not account for clustering or complex surveillance sampling. Overlapping interval endpoints must not be used as a formal test of change. A future inferential comparison should select a method appropriate to the surveillance design, dependence structure and estimand, and validate its assumptions.

## Release gate

Until representative outcome-labelled data and a pre-specified holdout evaluation exist:

- keep alert_rate and alert_change configurable and explicitly labelled heuristic;
- do not describe watch as a validated epidemiological alert or clinical recommendation;
- keep data_quality_score labelled as an uncalibrated engineering heuristic;
- do not claim sensitivity, specificity, predictive value, calibration, or out-of-sample validity;
- do not use outputs alone for treatment, infection-control, procurement, or public-health decisions.
