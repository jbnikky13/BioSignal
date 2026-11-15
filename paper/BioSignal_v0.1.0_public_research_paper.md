# BioSignal 0.1.0: An evolving evidence-aware framework for antimicrobial resistance data integration and exploratory surveillance

**Author:** Godam Sorbari Nichole  
**Affiliation:** Independent Researcher and Developer, BioSignal, Port Harcourt, Rivers State, Nigeria  
**Corresponding author:** godamsorbari13@gmail.com  
**ORCID:** https://orcid.org/0009-0000-5349-7784  
**Paper version:** 0.1.0  
**Development snapshot:** 15 November 2026  
**Project repository:** https://github.com/jbnikky13/BioSignal  
**Development record:** https://github.com/jbnikky13/BioSignal/pull/7  
**Status:** Public research and software-development paper; not a report of completed independent validation or a journal-ready clinical evaluation.

---

## Abstract

**Background:** Antimicrobial resistance (AMR) analysis draws on heterogeneous evidence, including aggregate antimicrobial susceptibility testing (AST), pathogen metadata, genome sequences, and computationally detected resistance-associated markers. These sources describe related but distinct phenomena. Their integration can create misleading conclusions if provenance, denominators, comparability, and evidence limitations are not preserved. BioSignal is an evolving research software project exploring an evidence-aware approach to AMR data integration and exploratory surveillance.

**Current implementation:** BioSignal is primarily implemented in Python, with Nextflow workflow orchestration and GitHub Actions automation. Its developing capabilities include structured observation ingestion and normalization, provenance tracking, data-quality checks, public pathogen/isolate metadata resolution, FASTA/FASTQ processing, GFF3 annotation parsing, AMRFinderPlus result ingestion, and structured evidence-aware reporting. Its central design principle is to keep aggregate phenotypic observations distinct from isolate-level genomic detections, while retaining detection scope, method, provenance, and review flags.

**Exploratory analysis:** Two author-supplied WHO GLASS bloodstream-infection dashboard exports were examined: *Escherichia coli*/ceftriaxone (114 country-year observations across 19 countries, 2018–2023) and *Acinetobacter* spp./colistin (66 observations across 11 countries, 2018–2023). Structural and denominator checks were repeated against the recovered files. A post-hoc next-year-change diagnostic produced weak and contrasting results: the *E. coli* holdout had sensitivity 100% and specificity 6.9%; the *Acinetobacter* holdout had sensitivity 0% and specificity 88.9%. These are exploratory diagnostics, not evidence of validated predictive performance.

**Conclusion:** BioSignal is an early-stage research prototype. This paper documents its current design, preliminary analyses, limitations, and open questions to invite scientific scrutiny and collaboration. It does not establish epidemiological calibration, clinical validity, or operational readiness. Independent review and externally sourced validation data are priorities for subsequent development.

**Keywords:** antimicrobial resistance; AMR surveillance; bioinformatics; data provenance; genomic evidence; WHO GLASS; AMRFinderPlus; reproducible research; open science.

## 1. Background and motivation

Antimicrobial resistance is a public-health challenge that requires reliable microbiological testing, surveillance systems, and careful interpretation of evidence. The World Health Organization's Global Antimicrobial Resistance and Use Surveillance System (GLASS) supports standardized national surveillance and reporting of AMR [1,2]. Public genomic resources also make pathogen metadata, genome assemblies, and computationally detected resistance-associated genes and mutations available for research.

These evidence sources are not interchangeable. An aggregate AST percentage describes a tested population under a particular sampling and laboratory context. A genomic marker detected in a sequence describes a computational finding for the submitted sequence and the reference database and method used. Detection of a gene or mutation does not, by itself, establish the susceptibility phenotype of an individual isolate. Genotype–phenotype comparison requires verified isolate linkage and appropriate interpretive context [3–5].

BioSignal was initiated to explore how structured AMR observations and genomic evidence might be processed together without collapsing their distinct meanings. The project emphasizes traceable inputs, explicit missingness, comparability checks, separation of evidence types, and reporting that carries caveats forward to downstream users.

This paper is a development snapshot and invitation to scientific review. It is not a claim that BioSignal is a validated diagnostic, clinical decision-support tool, or operational public-health alerting system.

### 1.1 Development objectives

The current objectives are to:

1. Establish a canonical representation for structured AMR observations from heterogeneous sources.
2. Preserve source provenance and metadata needed to assess comparability.
3. Support pathogen and isolate metadata resolution through public resources.
4. Process sequence and annotation inputs used in genomic AMR analysis.
5. Integrate genomic detection results while preserving detection type, method, scope, and review requirements.
6. Generate reproducible, evidence-aware reports.
7. Develop a transparent validation pathway requiring independent reference outcomes and expert review before performance claims are made.

## 2. Architecture and implementation

BioSignal is implemented primarily in Python. Nextflow orchestrates public-isolate workflows, while GitHub Actions supports automated software validation and reproducible execution [6]. The project is modular and remains under active development.

### 2.1 Structured observation ingestion

CSV ingestion and a canonical AMR observation schema support structured resistance observations. Source-specific fields are normalized into consistent representations while original labels and available source information are retained where possible. Optional metadata include specimen type, testing criteria, and laboratory method. Missing values remain unknown rather than being inferred.

### 2.2 Provenance and data-quality assessment

The project records source and dataset information and applies data-quality checks to incoming observations. Temporal comparisons use available organism, antimicrobial, region, source, and other metadata. Minimum-sample safeguards are intended to reduce misleading interpretations of small or poorly comparable observations.

The current `data_quality_score` is an uncalibrated engineering heuristic based on features such as sample size, metadata completeness, and observation-window length. It is not a probability, statistical confidence estimate, or validated measure of epidemiological quality. The comparison status `no_known_mismatch` means only that no mismatch was detected in the fields available to the software; it does not prove that two datasets are epidemiologically equivalent.

### 2.3 Pathogen and genomic metadata

The project integrates public NCBI metadata and supports isolate identifiers, BioSample-to-assembly resolution, and genome-package retrieval. Sequence-processing capabilities include FASTA parsing and quality checks, FASTQ parsing with Phred+33 quality handling, sequence-feature extraction, and GFF3 annotation parsing.

### 2.4 Genomic AMR evidence

BioSignal ingests AMRFinderPlus outputs into a normalized evidence representation. The reporting model is designed to preserve detection type, method, Core/Plus scope, locus metadata, reference information, and manual-review flags. AMRFinderPlus can identify acquired AMR genes and known resistance-associated point mutations, alongside selected virulence and stress-related findings [3–5]. These result categories must remain distinct.

BioSignal therefore restricts its AMR-hit representation to detections explicitly typed as AMR and does not automatically reinterpret virulence or stress findings as resistance evidence. Core and Plus detections are not silently merged into a single undifferentiated evidence class. Review flags are retained so that downstream reports do not present a computational detection as an expert-confirmed biological conclusion.

### 2.5 Evidence-aware reporting

The project generates structured JSON and Markdown reports from genomic evidence and associated metadata. Reports preserve the distinction between genomic detections and phenotypic AST observations. Aggregate AST data are not converted into individual-isolate susceptibility calls. Where isolate-level AST information or verified isolate matching is absent, that absence must remain explicit.

### 2.6 Workflow execution and reproducibility

A Nextflow public-isolate workflow connects metadata resolution, genome retrieval, sequence validation, AMRFinderPlus execution, and report generation. Lightweight validation and live public-isolate workflows are separated: stub-mode execution checks workflow structure and is not a biological analysis, while live execution depends on public resources and pinned tool/database information.

The project records relevant software versions and input checksums in workflow outputs. Complete archival retrieval and pinning of every reference database version remain areas for improvement. Some validation-readiness work is maintained in an open development pull request and is not necessarily part of the repository's default branch. The development record is linked above so readers can distinguish proposed changes from merged implementation.

## 3. Recovered WHO GLASS exploratory analysis

### 3.1 Source and scope

The exploratory exercise used two WHO GLASS dashboard CSV exports supplied by the author during development. The author reports downloading the files in late October 2026; the exact calendar date is not known. The dashboard landing page is recorded as https://www.who.int/initiatives/glass/, which links to the GLASS data visualization dashboard [7]. The exact chart/export view and source release/version were not captured in the CSV files.

The two resistance exports were:

- Bloodstream infection, *Escherichia coli* / ceftriaxone, 2018–2023: 114 country-year rows across 19 countries.
- Bloodstream infection, *Acinetobacter* spp. / colistin, 2018–2023: 66 country-year rows across 11 countries.

A third recovered export describing testing coverage by bacterial pathogen and antibiotic group was not used in these two analyses.

The two resistance files had no duplicate country-year keys or missing required parsed fields in the audit. Reported resistance percentages were consistent with resistant counts divided by interpretable AST counts within rounding precision. These checks establish internal consistency of the supplied exports; they do not establish representativeness, completeness, or comparability of national surveillance systems.

### 3.2 Descriptive interpretation

Pooled descriptive resistance percentages were calculated as the sum of resistant observations divided by the sum of interpretable AST observations among the countries represented in each export. These pooled values describe the observations in the supplied exports. They must not be interpreted as global population estimates, national prevalence estimates, or direct measures of an individual's probability of resistance.

### 3.3 Post-hoc next-year-change diagnostic

A preliminary diagnostic exercise defined the outcome as a resistance increase of at least five percentage points in the following year. Candidate thresholds were selected after inspecting the available data. The rule signalled when either the current resistance percentage or the previous-year change reached its selected threshold, subject to a minimum AST count of 20 in both the current and previous year. Development years were 2019–2020 and the holdout years were 2021–2022.

| Dataset | Current-rate threshold | Change threshold | TP | FP | TN | FN | Sensitivity | Specificity | PPV | Accuracy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| *E. coli* / ceftriaxone | 20% | 15 percentage points | 9 | 27 | 2 | 0 | 100% | 6.9% | 25% | 28.9% |
| *Acinetobacter* spp. / colistin | 30% | 15 percentage points | 0 | 2 | 16 | 4 | 0% | 88.9% | 0% | 72.7% |

The results are weak and contrasting. The *E. coli* rule identified all positive holdout observations but generated many false positives and very low specificity. The *Acinetobacter* rule missed all positive holdout observations. The small number of positive outcomes, repeated country observations, post-hoc outcome definition and threshold selection, and absence of cluster-aware uncertainty estimates limit interpretation. The analysis is not pre-registered, is not an independent external validation, and does not demonstrate reliable prediction of future resistance.

The purpose of reporting this diagnostic is to expose the current limitations and make the validation problem concrete—not to claim predictive success.

### 3.4 Reproducibility and source-data availability

The author has recovered files whose filters, 2018–2023 coverage, country-year row counts, and country counts match the datasets described above. Structural checks, descriptive summaries, and the documented post-hoc diagnostic were rerun against these files and reproduced the reported results.

Filenames, observed filters, and SHA-256 checksums are recorded in `data/examples/who-glass-source-manifest.csv`. The original download date is reported by the author as late October 2026, but the exact date and source release/version remain unverified. The raw CSV exports are not included in the repository pending review of applicable redistribution terms. Consequently, the results are reproducible from the author's recovered files but cannot yet be independently regenerated from repository contents alone. Readers should not treat the manifest as a substitute for access to the underlying source files.

## 4. Software verification and current development status

BioSignal uses automated tests and workflow checks to assess implementation integrity. Earlier recorded main-branch pipeline validation and public-isolate workflow runs completed successfully on 4 November 2026. A validation-readiness development branch also had a recorded successful pipeline validation on 9 November 2026. The current development pull request remains open and unmerged; a successful CI result on the final paper snapshot has not been confirmed.

These records demonstrate that specified software checks and workflow executions completed at those points in development. They do not constitute independent biological validation, establish epidemiological accuracy, or demonstrate clinical utility. A Nextflow stub-mode run validates workflow structure only; stub outputs are placeholders and contain no biological analysis.

## 5. Limitations and non-intended uses

The following limitations should guide interpretation:

1. **No independent reference cohort:** BioSignal does not yet have a sufficiently documented, independent cohort with expert-reviewed reference outcomes for evaluating surveillance signals.
2. **Exploratory GLASS scope:** The initial analysis is limited to two pathogen–antibiotic combinations and the countries represented in the supplied exports.
3. **Representativeness:** Country-level dashboard exports cannot automatically be treated as representative of national populations, WHO regions, or global AMR burden.
4. **Surveillance comparability:** Available metadata checks cannot account for all differences in patient populations, sampling practices, testing indications, laboratory methods, or duplicate-isolate handling.
5. **Uncalibrated heuristics:** Signal thresholds and the data-quality score are not calibrated statistical or epidemiological measures.
6. **Evidence linkage:** Genomic detection and phenotypic AST remain separate evidence streams unless verified isolate-level matching and appropriate interpretation are available.
7. **Source archival:** The raw WHO GLASS exports and complete source-view metadata are not yet archived with the code.
8. **Software status:** Some development work remains in an unmerged branch; the paper describes an evolving implementation, not a frozen, fully archived release.
9. **No operational evaluation:** There has been no demonstration of clinical benefit, improved patient outcomes, or reliable public-health alert performance.

BioSignal is not currently intended for clinical diagnosis, antimicrobial treatment selection, dose recommendation, patient management, or routine public-health alerting. Its outputs should not be used as the sole basis for clinical or public-health decisions.

## 6. External Scientific Review and Collaboration

BioSignal is being developed as an open, evolving research and software project. The author invites independent scientific feedback from researchers and practitioners in antimicrobial resistance surveillance, clinical microbiology, infectious diseases, epidemiology, bioinformatics, biostatistics, laboratory science, pharmacometrics, and digital health—particularly colleagues with experience in African and other resource-constrained settings.

This is an invitation for review, not a statement that independent review has already occurred. No external reviewer, institutional partner, or collaborating organization is being represented as having endorsed the project.

### 6.1 Priority questions for reviewers

**A. Scientific framing and evidence model**
- Does the separation of aggregate AST observations, isolate metadata, and genomic AMR detections adequately preserve the distinct meaning of each evidence stream?
- Are the Core/Plus detection distinctions, evidence typing, and review flags represented clearly enough for downstream scientific interpretation?
- What additional safeguards are needed to prevent gene detection from being mistaken for confirmed phenotypic resistance?

**B. Surveillance methods and data comparability**
- Are the proposed metadata fields sufficient to identify important comparability problems between surveillance observations?
- Which minimum denominators, uncertainty measures, sampling details, and surveillance-design variables should be required before comparing periods, sites, or countries?
- How should missingness, changes in testing coverage, and repeated country observations be handled?

**C. WHO GLASS exploratory analysis**
- Are the denominator checks and pooled descriptive summaries appropriate for the stated exploratory purpose?
- What is the most defensible interpretation of the two small, post-hoc holdout diagnostics?
- What alternative outcome definitions, baselines, or evaluation designs should be considered before any predictive claim is tested?

**D. Validation and benchmarking**
- What independent, provenance-documented datasets could support a meaningful validation study?
- What should constitute an appropriate reference standard and expert-adjudication process?
- Which existing tools or workflows should be included in a fair functional comparison, and what evaluation criteria should be used?
- Should evaluation be split by time, country, laboratory, or surveillance site to reduce information leakage?

**E. Usability and implementation**
- Which outputs would be most useful to microbiology laboratories, surveillance teams, researchers, and public-health practitioners?
- What additional provenance, audit-trail, or reproducibility information should be visible to users?
- What risks might arise when using this framework in settings with limited laboratory capacity or incomplete surveillance data?

### 6.2 Potential collaboration areas

The project is open to scoped collaboration in the following areas:

- **Scientific and clinical microbiology review:** review evidence interpretation, AMRFinderPlus result handling, and genotype–phenotype boundaries.
- **Epidemiology and biostatistics:** refine surveillance comparability criteria, outcome definitions, uncertainty estimation, and validation design.
- **Data and bioinformatics engineering:** improve source adapters, reference database versioning, workflow reproducibility, and test coverage.
- **Validation partnerships:** identify suitable de-identified or public datasets with documented provenance and expert-reviewed reference labels.
- **Regional research partnerships:** assess practical requirements and responsible use in African surveillance and laboratory contexts.
- **Pharmacometrics (future research direction):** explore whether appropriately governed exposure, MIC, dosing, and outcome datasets could support a separate future PK/PD research module. This is not part of the current implementation; BioSignal does not estimate drug exposure, recommend doses, or perform PK/PD simulations.

### 6.3 How to contribute feedback

Researchers may contribute through the public repository or by email. The external scientific feedback issue is available at https://github.com/jbnikky13/BioSignal/issues/new (search for “External scientific feedback and collaboration: BioSignal 0.1.0” in the repository issue list). Researchers who do not use GitHub may email godamsorbari13@gmail.com with the subject “BioSignal 0.1.0 — Scientific Feedback”. Feedback is most useful when it identifies the relevant section, describes the scientific or technical concern, explains its potential impact, and—where possible—suggests a reference, dataset, protocol, or test that could help resolve it.

Potential collaborators may use the repository to propose a focused review, validation exercise, benchmarking study, or implementation contribution. Any use of restricted or sensitive data must be discussed and governed before transfer or analysis. Please do not upload patient-identifiable or otherwise restricted data to public issues.

With permission, substantive contributions may be acknowledged in later project versions. Authorship will be discussed only where contributions meet the applicable authorship criteria. Reviewer identity, affiliation, comments, and endorsement will not be published without explicit permission.

## 7. Development roadmap

The next stage will prioritize:

1. Independent scientific review of the evidence model and interpretation boundaries.
2. Verification of WHO GLASS source-view metadata and applicable redistribution terms.
3. A reproducible, versioned software snapshot with a documented environment and archived source code.
4. Acquisition of an independent validation cohort with clear provenance, reference labels, and governance.
5. Pre-specified evaluation protocols, including time- or site-separated holdouts and cluster-aware uncertainty analysis.
6. Expert assessment of the data-quality heuristic using independently adjudicated labels.
7. Functional comparison with relevant surveillance and genomic analysis tools.
8. Iterative improvements based on documented reviewer feedback.

A future pharmacometrics research direction may be explored separately, but only with appropriate data, validated models, and specialist input.

## 8. Conclusion

BioSignal is an evolving African-led research software project exploring evidence-aware integration of AMR surveillance observations and genomic findings. Its current contribution is an engineering approach that emphasizes provenance, explicit uncertainty, separation of phenotypic and genomic evidence, and cautious reporting. The initial WHO GLASS analysis is a limited exploratory exercise whose diagnostic results demonstrate the need for stronger validation rather than established predictive capability.

Version 0.1.0 is published as a transparent development snapshot and an invitation to scientific scrutiny. The project seeks critical feedback, independent validation partners, and collaborators who can help determine whether and how the framework can become scientifically useful. Its future claims will depend on reproducible evidence, expert assessment, and independent evaluation.

## Availability and project information

- **Project:** BioSignal
- **Repository:** https://github.com/jbnikky13/BioSignal
- **Development record:** https://github.com/jbnikky13/BioSignal/pull/7
- **Paper version:** 0.1.0
- **Software archive/DOI:** Not yet available. This paper version does not imply that a tagged or DOI-archived software release has been created.
- **Primary language:** Python
- **Workflow orchestration:** Nextflow
- **Key external tools:** NCBI Datasets CLI and NCBI AMRFinderPlus
- **License:** The repository development metadata identifies Apache-2.0; readers should consult the repository's current LICENSE file for the authoritative licence text.
- **Data availability:** The two WHO GLASS resistance exports are held by the author and are not redistributed in the repository pending terms review. Their observed filters and checksums are recorded in the source manifest. The separate testing-coverage export was not used in the analyses reported here.

## Declarations

**Ethics approval and consent to participate:** The analyses described here use aggregate public surveillance exports and public pathogen/genome resources; no human participants were recruited and no patient-level data are described. Source-data provenance and any applicable data-use requirements remain subject to verification. This statement is not a substitute for an institutional ethics determination where one is required.

**Consent for publication:** Not applicable.

**Competing interests:** The author declares no competing interests.

**Funding:** The author received no specific funding for this work.

**Author contributions:** Godam Sorbari Nichole contributed to conceptualization, software development, methodology, investigation, data curation, and manuscript preparation. This statement should be checked against the final contribution record before any formal journal submission.

**Acknowledgements:** No external scientific reviewers or institutional collaborators are listed at this stage. Future acknowledgements will be added only with the relevant individuals' permission.

**Use of AI-assisted tools:** AI-assisted tools were used selectively as supporting aids during parts of software development, documentation, and manuscript editing. They did not replace the author’s direction of the project, scientific judgement, or responsibility for the work. The author determined the research questions and development priorities, reviewed and revised project outputs, and takes responsibility for the code, data handling, analyses, interpretation, references, and claims presented here. The use of such tools should not be taken to mean that the research design, scientific reasoning, or substantive project work was delegated to an AI system. This disclosure should be adapted to the requirements of any future publication venue.

**Author information:** Godam Sorbari Nichole is an independent researcher and developer based in Port Harcourt, Rivers State, Nigeria. Her interests include antimicrobial resistance surveillance, pharmacometrics, pharmaceutical systems, digital health, and the application of data science and artificial intelligence to healthcare challenges in Africa.

## References

1. World Health Organization. GLASS manual for antimicrobial resistance surveillance in common bacteria causing human infection. Geneva: WHO; 2023. ISBN 978-92-4-007660-0. https://www.who.int/publications/i/item/9789240076600.
2. World Health Organization. Global antibiotic resistance surveillance report 2025. Geneva: WHO; 2025. https://www.who.int/publications/i/item/9789240116337.
3. Feldgarden M, Brover V, Gonzalez-Escalona N, et al. AMRFinderPlus and the Reference Gene Catalog facilitate examination of the genomic links among antimicrobial resistance, stress response, and virulence. Sci Rep. 2021;11:12728. doi:10.1038/s41598-021-91456-0.
4. Feldgarden M, Brover V, Fedorov B, et al. Curation of the AMRFinderPlus databases: applications, functionality and impact. Microb Genom. 2022;8(6):000832. doi:10.1099/mgen.0.000832.
5. National Center for Biotechnology Information. AMRFinderPlus and NCBI Pathogen Detection documentation. https://www.ncbi.nlm.nih.gov/pathogens/antimicrobial-resistance/AMRFinder/.
6. Di Tommaso P, Chatzou M, Floden EW, Barja PP, Palumbo E, Notredame C. Nextflow enables reproducible computational workflows. Nat Biotechnol. 2017;35:316–319. doi:10.1038/nbt.3820.
7. World Health Organization. Global Antimicrobial Resistance and Use Surveillance System (GLASS): data visualization dashboard. https://www.who.int/initiatives/glass/.
