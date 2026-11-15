# WHO GLASS source-data recovery and reproducibility procedure

## Purpose

The exploratory results in the BioSignal manuscript were calculated from two WHO GLASS dashboard CSV exports supplied during development:

- Bloodstream infection, *Escherichia coli* / ceftriaxone, 2018–2023.
- Bloodstream infection, *Acinetobacter* spp. / colistin, 2018–2023.

The manuscript reports 114 country-year rows across 19 countries for the first export and 66 country-year rows across 11 countries for the second. These counts are historical descriptions in the manuscript, not substitutes for the source files.

The original exports are not currently present in the repository. Do not recreate them from the manuscript's reported counts or use a different export while presenting it as the original.

## Step 1 — Search for the original files

Check, in this order:

1. The device or computer used to download the WHO GLASS exports, including Downloads, Documents, Desktop, and project folders.
2. Cloud storage or backup folders used at the time, including Google Drive, iCloud Drive, OneDrive, or Dropbox.
3. Email attachments and messages where the CSV files may have been sent or shared.
4. GitHub repository history, branches, pull-request attachments, workflow artifacts, and local project backups.
5. Any notes, screenshots, browser download history, or analysis notebooks that record the exact dashboard filters.

Search filenames as well as likely terms such as `GLASS`, `Ecoli`, `ceftriaxone`, `Acinetobacter`, and `colistin`. Do not upload files containing patient-level or otherwise restricted data.

## Step 2 — Preserve and identify each candidate

For every candidate file:

- Keep an untouched original copy.
- Record its exact filename, file size, and modification date.
- Do not open and resave the original in spreadsheet software before calculating its checksum.
- Calculate a SHA-256 checksum and record it in `data/examples/who-glass-source-manifest.csv`.
- Record the WHO dashboard URL, retrieval date (UTC if known), source release/version if shown, exact filters, table or sheet used, geographic scope, year range, and denominator definition.
- Confirm that the organism, antimicrobial, infection/specimen type, and years match the manuscript description.

A matching filename alone is not proof that a file is the correct source export.

## Step 3 — If the original files cannot be found

Return to the official WHO GLASS dashboard and create new exports using the documented filters, if those filters can be reconstructed reliably.

Treat newly downloaded files as new source snapshots, not as the original historical files. Record the actual retrieval date, dashboard URL, visible release/version, all selected filters, and checksums. If a filter or source version cannot be established, record it as unknown rather than guessing.

Before retaining the manuscript's numerical claims, rerun the complete analysis against the recovered or newly exported files. If the outputs differ, update the manuscript and explain that the data snapshot or extraction differs. Do not silently retain old counts, pooled percentages, or diagnostic results.

If the historical filters cannot be reconstructed, the exploratory analysis must be described as not independently reproducible from the available materials until the source and analysis are rebuilt.

## Step 4 — Re-run and compare the analysis

For each source file:

1. Validate the expected columns and data types.
2. Check duplicate country-year keys and missing parsed fields.
3. Recalculate resistant counts divided by interpretable AST counts and verify rounding.
4. Recalculate the pooled descriptive percentage using the stated denominator.
5. Re-run the exploratory next-year-change diagnostic with its post-hoc status clearly stated.
6. Preserve scripts, environment details, logs, and generated outputs.
7. Compare every reported number with the manuscript and record discrepancies.

Do not describe country-level aggregate data as isolate-level or patient-level outcomes. Do not treat pooled dashboard percentages as global population estimates. Do not infer individual susceptibility from aggregate AST data or genomic marker detection.

## Step 5 — Redistribution and release

Check the applicable WHO terms and source attribution requirements before committing any source export. If redistribution is not permitted or is unclear, do not commit the CSV. Instead, publish the source manifest, retrieval instructions, checksum, analysis code, and derived outputs only where the applicable terms permit.

The release must make clear which inputs are publicly redistributable, which must be retrieved independently, and which exact snapshots were used to generate the reported results.

## Current status

- [ ] Original CSV exports located.
- [ ] Source identity and filters verified.
- [ ] SHA-256 checksums recorded in the manifest.
- [ ] Redistribution terms checked.
- [ ] Analysis rerun from preserved source files.
- [ ] Manuscript figures and numerical claims reconciled.
- [ ] Reproducibility materials reviewed on the final release commit.

Until these checks are complete, the manuscript must continue to disclose that the original exports are not archived in the repository and the exploratory analysis cannot be independently rerun from repository contents alone.
