# Reproducibility and release protocol

## Scope

This protocol distinguishes three different checks:

1. **Software verification:** unit tests, import checks, and Nextflow stub-mode compilation.
2. **Workflow execution:** a public NCBI isolate workflow completes with recorded tool/database versions and non-empty outputs.
3. **Scientific validation:** evaluation against independent, expert-reviewed reference outcomes using a pre-specified protocol.

Passing either of the first two does not establish the third.

## Software environment

- Python: >=3.11 (CI currently uses Python 3.12).
- Test runner: pytest >=8.
- Workflow engine: Nextflow 26.04.6 in the current CI configuration.
- Public-isolate workflow: NCBI Datasets CLI and NCBI AMRFinderPlus 4.2.7; the AMRFinderPlus database is initialized at run time and its version is recorded.
- Platform: CI runs on Ubuntu; local execution should use a compatible Linux environment.

Install and run the deterministic test suite:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pytest -q
```

Validate the Nextflow workflow without downloading genomes or performing biological analysis:

```bash
nextflow run workflows/public_isolate.nf \
  --biosample SAMN05215988 \
  --amrfinder_organism Escherichia \
  -stub-run
```

Stub-mode outputs are synthetic placeholders and must never be described as biological findings.

## Public-isolate execution

The manually dispatched GitHub Actions workflow installs NCBI Datasets CLI, Python, Nextflow, and AMRFinderPlus; runs the unit tests and AMRFinderPlus smoke tests; executes the public-isolate workflow; and checks the expected process trace and outputs. The workflow records the NCBI Datasets CLI version, AMRFinderPlus software version and database version, assembly summary, input archive checksum, and Nextflow reports/traces.

A successful run demonstrates that the defined workflow executed for that public accession under the recorded environment. It does not establish that genomic detections predict phenotype, nor does it validate epidemiological signals.

## WHO GLASS exploratory exports

The original WHO GLASS CSV exports underlying the current exploratory analysis are not currently committed to the repository. Therefore, the reported 114 and 66 country-year row counts and the post-hoc diagnostic metrics cannot yet be independently recomputed from repository contents alone.

Before claiming full reproducibility, the author should:

1. Re-download or recover the exact original exports used in the exploratory analysis.
2. Preserve each original file unchanged.
3. Complete `data/examples/who-glass-source-manifest.csv` with source URL, retrieval date, exact dashboard filters, source release/version if available, table name, and SHA-256 checksum.
4. Run the audit/importer and save normalized outputs as derived artifacts, with the exact software commit and command line.
5. Compare the regenerated summary with `docs/initial-who-glass-exploratory-evaluation.md`; explain any differences rather than silently replacing prior values.
6. Confirm the terms of use and redistribution permissions before committing raw exports. If redistribution is not permitted, deposit the source files in an appropriate repository or provide retrieval instructions and checksums.

Example checksum command:

```bash
sha256sum path/to/original-who-glass-export.csv
```

Example structural audit:

```bash
python scripts/audit_who_glass_export.py path/to/original-who-glass-export.csv \
  --normalized-csv reports/normalized-country-year.csv
```

Example regional summary:

```bash
python scripts/build_surveillance_summary.py path/to/original-who-glass-export.csv \
  --output-json reports/who-glass-summary.json \
  --country-year-csv reports/who-glass-country-years.csv \
  --region-year-csv reports/who-glass-region-years.csv
```

## Release and archival checklist

A citable release should not be tagged until all of the following are true:

- The intended licence is present in `LICENSE` and matches `pyproject.toml` and `CITATION.cff`.
- The package installs from a clean environment.
- The complete test suite and Nextflow stub-mode validation pass on the release commit.
- The live public-isolate workflow has a successful run attached to the exact release commit, with its artifact retained.
- The source-data manifest is complete for all reported analyses, and the GLASS exploratory summaries have been regenerated or clearly labelled as not independently reproducible.
- The repository README, manuscript, and release notes describe the same capabilities and limitations.
- A version tag is created only after review; the exact source archive is deposited in Zenodo (or another suitable archive) to obtain a DOI.
- The manuscript cites the exact version and DOI, not merely the moving default branch.

## Scientific-use boundary

BioSignal is a research and engineering prototype. It is not a diagnostic system, treatment recommender, calibrated epidemiological alert system, or operational public-health surveillance service. Gene/mutation detection is not equivalent to phenotypic resistance. Aggregate surveillance rates must not be used to infer patient-level susceptibility or dose selection.
