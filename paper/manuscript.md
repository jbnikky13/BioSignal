# BioSignal: Development of an evidence-aware framework for antimicrobial resistance data integration and exploratory surveillance

**Godam Sorbari Nichole**  
Independent Researcher and Developer, BioSignal

**Manuscript type:** Software development and methods  
**Development snapshot:** 10 November 2026  
**Software repository:** https://github.com/jbnikky13/BioSignal  
**Proposed software version:** 0.1.0 (release candidate; not yet archived)

## Abstract

**Background:** Antimicrobial resistance (AMR) surveillance draws on heterogeneous sources, including antimicrobial susceptibility testing (AST), pathogen metadata, genomic sequences, and computationally detected resistance markers. These sources describe related but distinct aspects of AMR and can be misinterpreted when provenance, denominators, and evidential limitations are not preserved.

**Objective:** To describe the development and current technical status of BioSignal, a research framework for integrating structured AMR observations with public pathogen metadata and genomic evidence while preserving provenance and interpretation boundaries.

**Methods:** BioSignal is implemented primarily in Python, with Nextflow workflow orchestration and GitHub Actions automation. Its modules support structured observation ingestion and normalization, provenance tracking, data-quality checks, pathogen/isolate metadata resolution, FASTA/FASTQ processing, GFF3 annotation parsing, AMRFinderPlus result ingestion, and evidence-aware reporting. Development verification includes automated tests, workflow compilation in stub mode, and public-isolate workflow execution.

**Results:** The implementation includes a canonical AMR observation model, deterministic exploratory signal logic, WHO GLASS dashboard-export parsing and audit utilities, NCBI BioSample-to-assembly resolution, sequence and annotation processing, AMRFinderPlus evidence harmonization, and JSON/Markdown reports. Two WHO GLASS bloodstream-infection exports supplied during development contained 114 country-year observations for *Escherichia coli*/ceftriaxone across 19 countries and 66 observations for *Acinetobacter* spp./colistin across 11 countries. A post-hoc next-year-change diagnostic showed substantial error and is not confirmatory validation. The main-branch validation and public-isolate workflow runs recorded on 4 November 2026 passed; a draft validation-readiness branch also passed its latest recorded pipeline check on 9 November 2026.

**Conclusion:** BioSignal demonstrates an evidence-aware engineering approach to AMR data integration and exploratory reporting. It remains an early research prototype. Independent expert-reviewed validation, complete source-data provenance, and archival reproducibility are required before epidemiological performance or operational utility can be claimed.

**Keywords:** antimicrobial resistance; AMR surveillance; bioinformatics; data provenance; genomic evidence; WHO GLASS; AMRFinderPlus; reproducible software.

## Background

Antimicrobial resistance is a major public-health challenge requiring reliable surveillance, laboratory capacity, and integration of epidemiological and microbiological evidence. The World Health Organization's Global Antimicrobial Resistance and Use Surveillance System (GLASS) provides a framework for standardized collection, analysis, and sharing of national AMR surveillance information [1,2].

Public genomic resources provide access to pathogen metadata, genome assemblies, and computationally detected resistance-associated genes and mutations. These findings are valuable but are not interchangeable with phenotypic AST results. Detection of a gene or mutation does not, by itself, establish the susceptibility phenotype of an individual isolate. This distinction is particularly important when genomic and phenotypic observations do not originate from the same isolate or lack verified matching identifiers [3–5].

BioSignal was initiated to explore how heterogeneous AMR observations and genomic evidence could be processed reproducibly and explainably. Development has focused on preserving source provenance, normalizing data without silently inferring missing values, maintaining distinctions between evidence types, and making analytical limitations visible in generated reports.

This paper documents the project's objectives, architecture, implemented capabilities, preliminary exploratory analysis, software verification, and current limitations. It does not claim that BioSignal is a validated diagnostic, clinical decision-support, or public-health alerting system.

### Project objectives

The development objectives are to: (1) establish a canonical representation for structured AMR observations from heterogeneous sources; (2) preserve provenance and metadata needed to assess comparability; (3) support pathogen and isolate metadata resolution through public resources; (4) process sequence and annotation inputs used in genomic AMR analysis; (5) integrate genomic detection results while preserving their type, method, scope, and review requirements; (6) generate reproducible, evidence-aware reports; and (7) establish a validation pathway requiring independent reference outcomes and expert review before performance claims are made.

## Implementation

BioSignal is implemented primarily in Python. Nextflow provides workflow orchestration for public-isolate experiments, while GitHub Actions supports automated validation and reproducible execution [6].

### 3.1 Data ingestion and normalization

The project includes CSV ingestion and a canonical AMR observation schema. Source-specific fields are normalized into consistent representations while original labels and source information are retained where possible. Optional metadata include specimen type, testing criteria, and laboratory method. Missing values remain unknown rather than being inferred. Comparability checks identify observable differences or missing metadata but do not establish epidemiological equivalence.

### 3.2 Provenance and data-quality assessment

BioSignal records source and dataset information and applies data-quality checks to incoming observations. Its data-quality score is an uncalibrated engineering heuristic, not a probability, confidence estimate, or validated measure of dataset quality. Temporal comparisons use normalized organism, antimicrobial, region, source, and other available metadata. Minimum-sample safeguards are intended to reduce misleading interpretations of small or poorly comparable observations.

### 3.3 Pathogen and genomic metadata

The project integrates public NCBI metadata and supports isolate identifiers, BioSample-to-assembly resolution, and genome-package retrieval. Sequence-processing capabilities include FASTA parsing and quality checks, FASTQ parsing with Phred+33 quality handling, sequence-feature extraction, and GFF3 annotation parsing.

### 3.4 Genomic AMR evidence

BioSignal integrates AMRFinderPlus outputs into a normalized evidence representation. The reporting model preserves detection type, method, Core/Plus scope, locus metadata, reference information, and manual-review flags. AMRFinderPlus identifies acquired AMR genes and known resistance-associated point mutations, as well as selected virulence and stress-related findings [3–5]. These categories must remain distinct. BioSignal therefore restricts its AMR-hit representation to detections explicitly typed as AMR and does not automatically interpret virulence or stress detections as resistance evidence.

### 3.5 Evidence-aware reporting

The project generates structured JSON and Markdown reports from genomic evidence and associated metadata. Reports preserve the distinction between genomic detections and phenotypic AST observations. Aggregate AST data are not converted into individual-isolate susceptibility calls, and missing isolate-level AST information is explicitly identified.

### 3.6 Workflow reproducibility

A Nextflow public-isolate workflow connects metadata resolution, genome retrieval, sequence validation, AMRFinderPlus execution, and report generation. GitHub Actions provides separate lightweight validation and public integration workflows. The live workflow records relevant software and database versions and input checksums. Complete archival retrieval and pinning of every reference database version remain areas for improvement. AI-assisted tools supported parts of manuscript drafting and software documentation; the author remains responsible for reviewing and verifying the final text, code, and scientific claims.

## Results

BioSignal has developed through successive engineering phases. The foundation phase established repository architecture, a canonical AMR observation schema, a deterministic signal engine, public source definitions, and unit tests. The data-engineering phase added CSV ingestion, WHO GLASS data interfaces, provenance, normalization, and data-quality assessment. The bioinformatics phase added pathogen metadata resolution, sequence processing, annotation parsing, AMRFinderPlus evidence integration, isolate matching, and reproducible public-isolate workflows.

At the development snapshot, the repository's main branch identifies bioinformatics as in progress. The intelligence and interface phases are not complete. Draft pull request #7 contains additional work on validation intake, expert feedback, descriptive WHO-region summaries, and documentation. Its latest recorded pipeline validation passed on 9 November 2026. Because this work remains unmerged, it is described as ongoing development rather than an established main-branch release.

## Discussion

### Relationship to existing resources

BioSignal is designed as an integration and evidence-reporting layer rather than a replacement for established surveillance or genomic detection resources. WHO GLASS provides standardized aggregate surveillance outputs but is not a general-purpose software framework for linking those outputs to isolate-level genomic evidence. NCBI AMRFinderPlus provides curated genomic resistance-marker detection, but it does not by itself perform BioSignal's aggregate AST ingestion, source-comparability checks, or cross-stream evidence-report generation. Nextflow provides workflow orchestration rather than AMR-specific interpretation. BioSignal combines selected capabilities around provenance, normalized observation handling, evidence separation, and reproducible reporting.

No head-to-head benchmark against existing AMR surveillance or genomic analysis platforms has been completed. The manuscript therefore makes no claim of superior accuracy, speed, coverage, or clinical utility. A comparative evaluation of functional coverage, usability, reproducibility, and output interpretation is a prerequisite for a stronger claim of software advance.

### Preliminary exploratory analysis

A preliminary exploratory exercise used two WHO GLASS dashboard CSV exports supplied during BioSignal development: bloodstream infection, *E. coli*/ceftriaxone, 2018–2023; and bloodstream infection, *Acinetobacter* spp./colistin, 2018–2023. The first export contained 114 country-year rows from 19 countries; the second contained 66 rows from 11 countries.

Initial integrity checks found no duplicate country-year keys or missing parsed fields in the reviewed exports. Reported resistance percentages were consistent with resistant counts divided by interpretable AST counts within rounding precision. These checks establish internal consistency of the supplied exports, not representativeness or comparability of the underlying surveillance systems.

Pooled descriptive resistance percentages were calculated as the sum of resistant observations divided by the sum of interpretable AST observations among countries represented in each export. They must not be interpreted as global population estimates.

A preliminary next-year-change diagnostic was also performed. Its provisional outcome definition was a reported increase of at least five percentage points in the following year. The outcome threshold was selected after inspecting the data, making the exercise post-hoc and exploratory rather than pre-registered or confirmatory.

For *E. coli*/ceftriaxone, the selected rule produced nine true positives and 27 false positives, with specificity of 6.9%. For *Acinetobacter* spp./colistin, it produced no true positives and four false negatives, with sensitivity of 0%. These findings do not demonstrate predictive performance. The small number of positive outcomes, repeated country observations, absence of cluster-aware uncertainty estimates, and post-hoc outcome definition limit interpretation. The exercise instead illustrates why threshold selection, data representativeness, denominator sensitivity, and independent validation must be addressed before an AMR signal can be considered reliable.

The original WHO GLASS CSV exports are not currently included in the repository. Consequently, the counts and exploratory diagnostic results in this section cannot yet be independently recomputed from the repository contents alone. The repository now includes a source-data manifest template and a reproducibility protocol specifying the metadata, checksums, and rerun steps required before a fully reproducible archival release.

### Software and workflow verification

The repository uses automated tests and workflow checks to assess implementation integrity. The latest recorded main-branch pipeline validation completed successfully on 4 November 2026. The latest recorded public-isolate execution on main also completed successfully on that date. An earlier public-isolate run failed during report acceptance checks; a subsequent order-sensitive validation correction was followed by a successful run. The latest pipeline validation associated with the draft validation-readiness pull request completed successfully on 9 November 2026.

These results demonstrate that specified software checks and recorded workflow executions completed. They do not constitute independent biological validation, establish epidemiological accuracy, or demonstrate clinical utility. A Nextflow stub-mode run validates workflow structure only; stub outputs are placeholders and contain no biological analysis.

### Limitations

Several limitations remain. First, the project does not yet have a sufficiently documented independent cohort with expert-reviewed reference outcomes for evaluating its surveillance signals. Second, the initial WHO GLASS analysis is post-hoc and limited to two pathogen–antibiotic combinations and the countries represented in the supplied exports. Third, the reviewed country-level exports cannot be assumed to represent national populations, WHO regions, or global AMR burden. Fourth, available metadata checks cannot account for all differences in patient populations, sampling practices, laboratory methods, testing indications, or duplicate-isolate handling. Fifth, signal thresholds and the data-quality score have not been established as calibrated statistical or epidemiological measures. Sixth, genomic detection and phenotypic AST remain separate evidence streams unless verified isolate-level matching and appropriate interpretation are available. Seventh, the source CSV exports underlying the exploratory analysis are not yet archived with complete provenance. Finally, the project is not approved for clinical diagnosis, treatment decisions, public-health alerting, or routine operational surveillance.

### Future work

The next development stage should prioritize expert review of scientific assumptions and the evidence model; acquisition of an independently sourced, provenance-documented validation cohort; pre-specification of outcome definitions and evaluation protocols; site- or country-level holdouts and cluster-aware uncertainty analysis; independent assessment of the data-quality heuristic using expert-adjudicated quality labels; broader pathogen–antibiotic coverage and explicit representativeness assessments; and improved archival reproducibility of reference databases and software environments.

An adjacent research direction is pharmacometrics, particularly pharmacokinetic/pharmacodynamic (PK/PD) modelling of antimicrobial exposure, efficacy, and resistance emergence. Such work could eventually complement AMR surveillance by examining how antimicrobial exposure relates to microbiological outcomes and by supporting model-informed dose research. It is not part of the current BioSignal implementation, and BioSignal does not estimate drug exposure, recommend doses, or perform PK/PD simulations. Any future integration would require appropriate concentration, MIC, dosing, patient covariate, and outcome data, validated models, and pharmacometric expertise [7].

## Conclusions

BioSignal has progressed from a structured AMR data-processing concept to an engineering prototype that integrates surveillance observations, public pathogen metadata, genomic analysis, and evidence-aware reporting. Its central design principle is to preserve distinctions between evidence types and make uncertainty and limitations explicit. The initial exploratory analysis illustrates both the potential usefulness and the risks of deriving surveillance signals from heterogeneous country-level data. The project is not yet scientifically calibrated or clinically validated. Its immediate priorities are source-data archival, independent expert review, validation data, and reproducible evaluation before stronger claims about surveillance performance can be made.

## Availability and requirements

- **Project name:** BioSignal
- **Project home page:** https://github.com/jbnikky13/BioSignal
- **Archived version:** Not yet available; a versioned archive and DOI are release gates.
- **Operating systems:** Linux CI environment; compatible local environments should be verified by the user.
- **Programming language:** Python 3.11 or later; Nextflow for the public-isolate workflow.
- **Other requirements:** pytest for tests; Nextflow 26.04.6 for workflow execution; NCBI Datasets CLI and NCBI AMRFinderPlus 4.2.7 for the live public-isolate workflow.
- **License:** Apache-2.0 (repository metadata and release-preparation branch).
- **Restrictions:** No additional non-academic-use restriction is intended under the stated software licence.

## List of abbreviations

AMR, antimicrobial resistance; AST, antimicrobial susceptibility testing; CI, continuous integration; GLASS, Global Antimicrobial Resistance and Use Surveillance System; PK/PD, pharmacokinetics/pharmacodynamics.

## Declarations

### Ethics approval and consent to participate

The described exploratory analyses use aggregate public surveillance exports and public pathogen/genome resources; no human participants were recruited and no patient-level data are described. **Author must verify all source-data provenance and the target journal's ethics requirements before submission.**

### Consent for publication

Not applicable.

### Availability of data and materials

The source code is publicly browsable at https://github.com/jbnikky13/BioSignal. The WHO GLASS dashboard exports used in the initial exploratory analysis are not currently included in the repository. Their exact source release, dashboard filters, retrieval dates, and checksums must be recovered and recorded before the reported exploratory results can be independently reproduced. The repository's source-manifest template and reproducibility protocol specify the information required. Public NCBI resources are identified by BioSample and assembly accessions in the workflow outputs. A DOI for an archived software release is not yet available.

### Competing interests

**Author confirmation required.** If none, replace this paragraph with: “The author declares that there are no competing interests.”

### Funding

**Author confirmation required.** If no specific funding was received, replace this paragraph with: “The author received no specific funding for this work.”

### Authors' contributions

Godam Sorbari Nichole: conceptualization, software, methodology, investigation, data curation, visualization, and writing—original draft. The author should verify this contribution statement against the actual contribution record before submission.

### Acknowledgements

Not applicable unless individuals or organizations who have agreed to be acknowledged are added.

### Authors' information

Godam Sorbari Nichole is an independent researcher and developer working at the intersection of pharmacy, antimicrobial resistance, and health technology. **Author to confirm the preferred biographical wording and affiliation address.**

### Corresponding author

**Author to provide a working email address and ORCID if available/required.**

### Use of AI-assisted tools

**Author to review and disclose** the use of AI-assisted tools for drafting, coding, or analysis in accordance with the selected journal's current policy. AI tools are not authors.
## References

1. World Health Organization. GLASS manual for antimicrobial resistance surveillance in common bacteria causing human infection. Geneva: WHO; 2023. ISBN 978-92-4-007660-0. https://www.who.int/publications/i/item/9789240076600. Accessed 10 Nov 2026
2. World Health Organization. Global antibiotic resistance surveillance report 2025. Geneva: WHO; 2025. https://www.who.int/publications/i/item/9789240116337. Accessed 10 Nov 2026
3. Feldgarden M, Brover V, Gonzalez-Escalona N, et al. AMRFinderPlus and the Reference Gene Catalog facilitate examination of the genomic links among antimicrobial resistance, stress response, and virulence. Sci Rep. 2021;11:12728. doi:10.1038/s41598-021-91456-0.
4. Feldgarden M, Brover V, Fedorov B, et al. Curation of the AMRFinderPlus databases: applications, functionality and impact. Microb Genom. 2022;8(6):000832. doi:10.1099/mgen.0.000832.
5. National Center for Biotechnology Information. AMRFinderPlus and NCBI Pathogen Detection documentation. https://www.ncbi.nlm.nih.gov/pathogens/antimicrobial-resistance/AMRFinder/. Accessed 10 Nov 2026
6. Di Tommaso P, Chatzou M, Floden EW, Barja PP, Palumbo E, Notredame C. Nextflow enables reproducible computational workflows. Nat Biotechnol. 2017;35:316–319. doi:10.1038/nbt.3820.
7. Mouton JW, Dudley MN, Cars O, Derendorf H, Drusano GL. Standardization of pharmacokinetic/pharmacodynamic (PK/PD) terminology for anti-infective drugs: an update. J Antimicrob Chemother. 2005;55(5):601–607. doi:10.1093/jac/dki079.
