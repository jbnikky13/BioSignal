# Submission and release gate — BioSignal

## Current recommendation

**Preferred journal to investigate:** BMC Bioinformatics, Software Article. The journal is currently indexed for MEDLINE according to the NLM Catalog. This is a target recommendation, not a guarantee of editorial fit or acceptance.

BMC Bioinformatics software articles are expected to describe a tool with broad utility and a significant advance, make the software available for anonymous reviewer testing, and discuss functionality/performance relative to comparable tools. The current manuscript is transparent that no head-to-head benchmark has been completed; this is a material gap to address before submission.

## Author confirmations required

- [ ] Confirm full affiliation address (city and country) and corresponding-author email.
- [ ] Provide ORCID if available.
- [ ] Confirm funding statement.
- [ ] Confirm competing-interests statement.
- [ ] Verify ethics statement and the exact provenance/terms of all public datasets.
- [ ] Verify CRediT contributions.
- [ ] Confirm acknowledgements and obtain permission from anyone named.
- [ ] Review AI-assisted-tool disclosure against the journal's current policy.
- [ ] Read and approve the complete manuscript and supplementary materials.

## Scientific and reproducibility requirements

- [ ] Recover the exact two WHO GLASS CSV exports used in the pilot.
- [ ] Record dashboard URL, retrieval date, selected filters, source release/version (if available), table name, and SHA-256 checksum in `data/examples/who-glass-source-manifest.csv`.
- [ ] Confirm redistribution permissions. Do not commit source data unless permitted.
- [ ] Re-run both audits and the exploratory calculations from the preserved originals.
- [ ] Compare regenerated outputs with the values reported in the manuscript and explain any discrepancy.
- [ ] Conduct a functional comparison with relevant tools/resources (e.g., WHO GLASS, NCBI AMRFinderPlus, and comparable AMR data-integration tools); do not imply a performance advantage without evidence.
- [ ] Obtain independent AMR expert review of the interpretation boundaries and proposed validation protocol.
- [ ] Keep pharmacometrics/PK-PD explicitly described as future complementary work; it is not implemented in BioSignal.

## Software release requirements

- [ ] Confirm all code and documentation included in the Apache-2.0 release are owned by or licensed to the project owner and that third-party content has compatible terms.
- [ ] Run a clean install and the full pytest suite on the final release commit.
- [ ] Run the Nextflow stub workflow on the final release commit.
- [ ] Run the public-isolate workflow on the final release commit and retain the artifact, tool/database versions, checksum, trace, and report.
- [ ] Review all tests and workflow checks after the latest commits; the 9 November 2026 passing run predates the release-preparation commits.
- [ ] Review the release archive and citation metadata.
- [ ] Create a version tag only after all checks pass.
- [ ] Archive the exact tagged source in Zenodo (or an equivalent repository) and obtain a DOI.
- [ ] Insert the DOI and exact version into the manuscript and citation metadata.

## Submission files

- [x] Manuscript draft in Markdown.
- [x] Editable Word manuscript draft.
- [x] Software citation metadata.
- [x] Licence text on the release-preparation branch.
- [x] Reproducibility protocol and source-manifest template.
- [ ] Final manuscript with all author declarations resolved.
- [ ] DOI-backed archived source release.
- [ ] Supplementary source code/test data package suitable for anonymous review.
- [ ] Cover letter tailored to the final target journal.

## Journal references checked on 10 November 2026

- BMC Bioinformatics software article criteria: https://link.springer.com/journal/12859/submission-guidelines/software-article
- BMC Bioinformatics general submission guidance and current APC: https://link.springer.com/journal/12859/submission-guidelines
- NLM FAQ on checking current MEDLINE indexing: https://www.nlm.nih.gov/medline/medline_faq.html
- NLM Catalog record for BMC Bioinformatics: https://www.ncbi.nlm.nih.gov/nlmcatalog?term=1471-2105%5BISSN%5D
