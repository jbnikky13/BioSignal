# BioSignal expert feedback and scientific collaboration pathway

**Status:** proposed; no external expert approval is implied.

## Purpose

Create a traceable route for AMR epidemiologists, clinical microbiologists, bioinformaticians, laboratory quality specialists, and public-health surveillance practitioners to review BioSignal's assumptions before any scientific validation or operational claims.

## 1. Review package

Share the following together, not as an isolated code link:
1. AMRIF technical concept note.
2. Scientific validation plan.
3. WHO GLASS validation protocol.
4. Country-held-out evaluation protocol.
5. AMRFinderPlus evidence interpretation.
6. A reproducible public example and the exact commit SHA reviewed.

## 2. Review questions

Ask reviewers to comment on:
- Whether the intended use and unit of analysis are sufficiently precise.
- Whether AST denominators, resistant counts, specimen groups, and missingness are handled appropriately.
- Whether source, laboratory method, testing criteria, specimen, country/region, and time metadata are adequate for comparisons.
- Whether the proposed reference outcome is independent of BioSignal's signal rule and scientifically meaningful.
- Whether country/site holdout, temporal separation, and clustering controls are appropriate.
- Whether genomic evidence is correctly separated from phenotypic resistance and whether manual-review flags are sufficient.
- Which organisms, antimicrobials, specimen types, and geographies should be prioritized for a first pilot.
- Which results, caveats, and intended-use limits must accompany any dashboard.

## 3. Suggested reviewer roles

Seek at least one AMR epidemiologist or surveillance scientist, one clinical microbiologist/AST laboratory specialist, and one bioinformatician familiar with AMRFinderPlus or bacterial genomics. Where possible, include a data-governance or public-health informatics reviewer.

A single reviewer may comment on multiple areas, but their role and scope should be recorded. Do not imply institutional endorsement from an individual's informal feedback.

## 4. Feedback workflow

1. Send the concept note and repository link with a short request for a 30-minute technical review or written comments.
2. Ask reviewers to identify their relevant expertise and any conflict of interest.
3. Record feedback in docs/review/feedback-register.md using a pseudonymous reviewer ID unless the reviewer consents to public attribution.
4. Classify each item as accepted, partially accepted, deferred, or not adopted; record rationale, affected files, and follow-up owner.
5. Update the protocol only after resolving scientific questions. Record the version and date.
6. Obtain explicit expert approval of the outcome definition and holdout design before any confirmatory evaluation.
7. Keep data-quality-score review separate: it requires blinded labels against an agreed quality rubric, not AMR event labels.

## 5. Minimum evidence before evaluation

Do not run a confirmatory evaluation until dataset release and retrieval provenance, source coverage, inclusion/exclusion rules, denominators, deduplication policy, stable surveillance-unit identifiers, independent outcome labels, protocol freeze, and preselected untouched holdout units have been reviewed.

If a condition is missing, perform structural or descriptive analysis only and label it accordingly.

## 6. Outreach message

Use this as a starting point; personalize the recipient and context before sending.

> I am developing BioSignal, an early-stage African-led open-source research prototype focused on reproducible AMR data handling, genomic evidence reporting, and transparent surveillance summaries. I would value expert feedback on its scientific assumptions, particularly the separation of AST and genomic evidence, dataset comparability, and the design of an independent validation protocol. I have prepared a short technical concept note and would welcome a brief technical review or written comments. The project is not presented as clinically validated or ready for operational use.

## 7. Governance

Do not upload private laboratory data, patient data, reviewer contact details, or confidential feedback to the public repository. Obtain permission before naming reviewers or institutions. Record approvals with date, scope, role, and reference; do not treat informal comments as formal approval.
