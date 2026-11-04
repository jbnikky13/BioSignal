# Combined AMRFinderPlus public-isolate analysis

## Analysis design

The public-isolate workflow now produces two independent AMRFinderPlus reports from the same versioned NCBI assembly package:

1. `amrfinderplus_nucleotide_baseline.tsv`: the existing nucleotide-only `--plus -n` analysis, retained as a comparator.
2. `amrfinderplus_combined.tsv`: combined `--plus -n -p -g` analysis using the genomic nucleotide FASTA, annotated protein FASTA, and matching GFF3 file.

The combined mode uses protein-level searches, including HMMER, while retaining nucleotide-level translated searches, mutation screening, and internal-stop detection. The NCBI Datasets package is requested with `--include genome,protein,gff3`.

## Input validation

Before AMRFinderPlus runs, BioSignal checks that:

- all three NCBI inputs exist and are non-empty;
- the GFF has nine-column feature rows;
- GFF contig identifiers occur in the nucleotide FASTA;
- at least one GFF `Name=` identifier matches a protein FASTA record identifier.

The validation deliberately fails closed when the NCBI package does not provide a compatible annotation relationship. It does not silently fall back to nucleotide-only mode.

The NCBI package uses the default GenBank/RefSeq GFF identifier convention. If a future data source uses external PGAP output or another annotation convention, configure and validate the appropriate AMRFinderPlus annotation format rather than assuming compatibility.

## Summary and interpretation

`amrfinderplus_summary.md` reports row counts separately by AMRFinderPlus `Scope`, `Type`, and `Method`. It preserves multiple loci that share an element symbol and flags `INTERNAL_STOP`, `PARTIAL`, and `PARTIAL_CONTIG_END` rows for manual review.

- Core and Plus scopes must not be conflated.
- Plus-scope entries can include virulence, stress, general efflux, and AMR-associated families whose phenotype effect may be uncertain.
- A gene or mutation detection is not proof of phenotypic resistance, expression, or treatment response.
- Identity, reference coverage, method, contig context, and isolate phenotype require separate review.
- This automated summary is research evidence handling, not clinical interpretation.

## Provenance and reproducibility

The artifact includes the NCBI Datasets CLI version, assembly summary, SHA-256 checksum of the downloaded package, AMRFinderPlus executable/software version, and AMRFinderPlus database version.

The software is pinned to AMRFinderPlus 4.2.7 in the GitHub Actions workflow. The database is updated at run time and its exact version is recorded, but is **not yet pinned to an archived database release**. Therefore, reruns may differ as the NCBI reference database evolves. Do not describe the run as fully database-reproducible until archived database retrieval and version enforcement are implemented.

## Acceptance gate

The live workflow is accepted only when all Nextflow processes exit successfully, both reports are non-empty and have the expected columns, the assembly manifest matches the requested BioSample, the provenance files exist, and the interpretation summary contains the scientific caveats.

The smoke test exercises both nucleotide-only and combined command modes using NCBI's own test input files. It does not replace the live public-isolate run. A successful stub workflow is only a graph/compile check; it is not a biological analysis.
## Downstream ingestion and reporting safeguards

The Python ingestion layer preserves the AMRFinderPlus `Scope` field (`core`, `plus`, or explicit `unknown`) separately from `Type` (for example, `AMR`, `VIRULENCE`, or `STRESS`). It accepts the current TSV headers (`Protein id`, `Closest reference accession`, `% Coverage of reference`, and `% Identity to reference`) as well as legacy aliases. Coordinates, contig, reference accession, method, identity, coverage, and review state are retained in normalized evidence.

Rows with methods `INTERNAL_STOP`, `PARTIAL`, or `PARTIAL_CONTIG_END` carry an explicit manual-review flag and reason. Rows are not deduplicated by element symbol; distinct loci remain distinct evidence records.

Only rows explicitly typed `AMR` are included in the report's AMR-hit list. Plus-scope virulence and stress findings remain visible as genomic detections but are not mislabeled as AMR hits. The live workflow also writes `amrfinderplus_evidence.json` through the same normalized parser. It retains each detection's scope, type, method, reference accession, identity, coverage, genomic location, and review flags; the workflow validator checks row counts and review-flag consistency.

Aggregated AST observations are never converted into an individual isolate's resistant/susceptible phenotype. They are reported as aggregate resistance proportions only. No genotype-phenotype linkage is made unless compatible isolate-level identifiers and evidence are available and verified. A gene or mutation detection is never presented as confirmed phenotypic resistance.
