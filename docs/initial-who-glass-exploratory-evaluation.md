# Initial WHO GLASS AMR exploratory evaluation

**Status:** exploratory diagnostic only; not scientific validation.

## Source and scope

This report summarizes two WHO GLASS dashboard CSV exports supplied for BioSignal development:

- Bloodstream infection, *Escherichia coli* / ceftriaxone, 2018–2023.
- Bloodstream infection, *Acinetobacter* spp. / colistin, 2018–2023.

The export rows contain country/territory, WHO region, year, total specimen isolates, interpretable AST count, resistant count, and percent resistant. The raw CSVs are not committed here; retain their original source exports and release/context metadata alongside any reproducible rerun.

## Data checks

| Export | Country-year rows | Countries | Years | Duplicate country-years | Missing parsed fields |
|---|---:|---:|---|---:|---:|
| *E. coli* / ceftriaxone | 114 | 19 | 2018–2023 | 0 | 0 |
| *Acinetobacter* spp. / colistin | 66 | 11 | 2018–2023 | 0 | 0 |

Both are balanced panels for the included countries. The reported percent resistant agrees with 100 × resistant / interpretable AST within rounding precision. No row had zero interpretable AST, resistant counts above interpretable AST, or interpretable AST above total specimen isolates.

These checks establish internal consistency only. They do not establish representativeness, comparability of laboratory methods, duplicate-isolate handling, or suitability for clinical decision-making.

## Descriptive results

Pooled rates below are sum(resistant) / sum(interpretable AST) within the countries in each export. They are not global population estimates.

| Year | *E. coli* / ceftriaxone | *Acinetobacter* spp. / colistin |
|---|---:|---:|
| 2018 | 20.12% | 3.98% |
| 2019 | 23.47% | 4.12% |
| 2020 | 22.09% | 4.39% |
| 2021 | 24.60% | 5.89% |
| 2022 | 27.53% | 1.89% |
| 2023 | 28.26% | 1.31% |

For *E. coli* / ceftriaxone, 12 of 19 countries had a higher reported percentage in 2023 than 2018; 7 had a lower percentage. The country-level 2018–2023 change ranged from −17.08 to +18.53 percentage points. In 2023, country-level rates ranged from approximately 10.95% to 85.13%.

For *Acinetobacter* spp. / colistin, 7 of 11 countries had a higher reported percentage in 2023 than 2018, 3 had a lower percentage, and 1 was unchanged. The pooled rate fell after its 2021 peak; this alone cannot distinguish a true epidemiological change from differences in reporting, testing, or country contributions.

Pooled percentages can conceal major between-country differences and are sensitive to the AST denominators of the reporting countries. Avoid labelling these pooled rates as global estimates.

## Exploratory next-year-change diagnostic

For a preliminary diagnostic only, each country-year from forecast origin years 2019–2022 was represented by:
- current resistance proportion;
- prior-year resistance proportion;
- current and prior interpretable AST counts.

The provisional binary outcome was a reported resistance increase of at least 5 percentage points in the following year. Development forecast origins were 2019–2020 (38 *E. coli* country-years; 22 *Acinetobacter* country-years). Holdout forecast origins were 2021–2022, targeting outcomes observed in 2022–2023 (38 and 22 country-years, respectively).

Threshold selection used the existing candidate grid (current rate 10%, 20%, 30%; change 5, 10, 15 percentage points), minimum interpretable AST count 20, maximizing Youden's J on development rows with ties broken toward higher thresholds. The provisional 5-point outcome definition was chosen for exploration after the dataset had been inspected; it was not pre-registered. Consequently, this is **post-hoc exploratory diagnostics**, not an untouched, confirmatory or independent validation.

### Held-out results

| Metric | *E. coli* / ceftriaxone | *Acinetobacter* spp. / colistin |
|---|---:|---:|
| Holdout observations | 38 | 22 |
| Positive outcomes | 9 | 4 |
| Selected current-rate threshold | 20% | 30% |
| Selected change threshold | 15 percentage points | 15 percentage points |
| True positives | 9 | 0 |
| False positives | 27 | 2 |
| True negatives | 2 | 16 |
| False negatives | 0 | 4 |
| Sensitivity | 100% | 0% |
| Specificity | 6.9% | 88.9% |
| Positive predictive value | 25% | 0% |
| Accuracy | 28.9% | 72.7% |

The *E. coli* rule generated many false alarms; the *Acinetobacter* rule missed all four provisional positive outcomes. A majority-class all-negative baseline would have accuracy 76.3% and 81.8%, respectively, but accuracy alone is not an appropriate selection criterion for an alerting system with imbalanced outcomes.

These metrics should not be treated as stable estimates: rows repeat countries across years, the number of positive outcomes is small, and there was no cluster-aware uncertainty analysis. The outcome threshold is not clinically justified. The same-source future change is a retrospective forecasting target, not independent clinical adjudication.

## Conclusions and required next steps

1. Do not claim scientific calibration or representative out-of-sample validation from this exercise.
2. Preserve country-specific series and test for denominator sensitivity; do not use the pooled trend as a global estimate.
3. Define and register an outcome with AMR domain experts before the next evaluation; justify the clinically or operationally meaningful change threshold.
4. Expand to more pathogen–antibiotic combinations and countries, and evaluate transportability with country/site-level holdouts and cluster-aware uncertainty.
5. Evaluate the data-quality heuristic separately using blinded expert quality labels. These AMR outcome exports do not contain such labels and therefore cannot calibrate the quality score.
6. Keep the PR in draft until the evaluation protocol, source release, coverage/representativeness assessment, and limitations are reviewed. No merge or deployment is implied by this report.
