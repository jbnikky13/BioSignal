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


## Implemented evaluation harness

BioSignal now includes `src/biosignal/calibration.py` with:
- strict validation of reference labels and their source/protocol provenance;
- chronological development/holdout splitting;
- development-only threshold selection using a pre-specified Youden's J objective;
- frozen-threshold holdout evaluation;
- sensitivity, specificity, PPV, NPV, false-positive rate, denominators, and Wilson intervals for selected proportions;
- AUROC for evaluating whether the uncalibrated data-quality score ranks independently adjudicated acceptable-quality observations above unacceptable-quality observations.

The blank schema template is `data/examples/calibration_template.csv`. It intentionally contains no fabricated records or outcomes. These functions are evaluation infrastructure, not evidence of calibration. Do not run threshold selection on holdout data or report performance until a real dataset has passed provenance, coverage, and label-quality review.

## Data-quality score evaluation

The existing `data_quality_score` is not a probability and must not be probability-calibrated merely by renaming it. To evaluate it, experts blinded to the score should independently label records against a documented data-quality rubric (including coverage, representativeness, denominator validity, deduplication, and testing comparability). Use development data to choose any score cutoff, then evaluate discrimination and error rates on a separate chronological and preferably external-site holdout. If a probability is ultimately needed, fit a pre-specified mapping on development data and evaluate calibration only on untouched holdout data, with calibration plots, Brier score, uncertainty intervals, and subgroup analysis.

## Candidate public data sources

- WHO GLASS provides official national AMR surveillance and a global dashboard; it is a suitable candidate for aggregate trend evaluation where the downloaded release exposes compatible denominators and time points. Source: https://www.who.int/data/gho/data/themes/topics/topic-details/GHO/global-antimicrobial-resistance-surveillance-system-glass
- ECDC EARS-Net provides public descriptive surveillance results and historical reports for invasive isolates. Its documentation explicitly warns about variation in coverage, sampling, and laboratory practices, so it is not automatically representative of other care settings or countries. Source: https://www.ecdc.europa.eu/en/about-us/networks/disease-networks-and-laboratory-networks/ears-net-data
- Public aggregate sources such as NovAMR can support exploratory checks, but its documentation describes heterogeneous institutions, years, specimen groups, methods, and care settings. It must not be treated as a homogeneous validation cohort without filtering and provenance review. Source: https://www.novamr.org/data

No external data have yet been ingested or scored in this PR. The next evidence-producing step is to obtain a documented dataset release with stable country/site-time series, usable denominators, source coverage metadata, and an outcome definition that was fixed before threshold selection. If those conditions are not met, the result must remain an implementation-only validation, not scientific validation.
