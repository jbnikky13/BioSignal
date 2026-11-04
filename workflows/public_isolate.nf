nextflow.enable.dsl=2

params.biosample = "SAMN05215988"
params.amrfinder_organism = "Escherichia"
params.report_organism = "Escherichia coli"
params.outdir = "results"
params.python_executable = "python"

process RESOLVE_ASSEMBLY {
    publishDir params.outdir, mode: "copy", overwrite: true
    input:
    val biosample
    output:
    tuple path("assembly_manifest.json"), path("assembly_accession.txt")
    script:
    """
    echo "Python interpreter: ${params.python_executable}"
    test -x "${params.python_executable}"
    "${params.python_executable}" -c 'import biosignal.resolve_assembly'
    "${params.python_executable}" -m biosignal.resolve_assembly "${biosample}" --output assembly_manifest.json
    "${params.python_executable}" -c 'import json; print(json.load(open("assembly_manifest.json", encoding="utf-8"))["assembly_accession"])' > assembly_accession.txt
    """
    stub:
    """
    echo '{"biosample_accession":"${biosample}","assembly_accession":"GCA_STUB.1"}' > assembly_manifest.json
    echo "GCA_STUB.1" > assembly_accession.txt
    """
}

process DOWNLOAD_GENOME {
    input:
    tuple path(manifest), path(assembly_accession_file)
    output:
    path "dataset"
    script:
    """
    set -Eeuo pipefail
    assembly=ESCAPED_$(tr -d '[:space:]' < ${assembly_accession_file})
    test -n "ESCAPED_$assembly"
    if [[ ! "ESCAPED_$assembly" =~ ^(GCA|GCF)_[0-9]+\. [0-9]+ESCAPED_$ ]]; then
      echo "Invalid NCBI assembly accession: ESCAPED_$assembly" >&2
      exit 1
    fi
    echo "Downloading NCBI assembly with genome, protein and GFF3: ESCAPED_$assembly"
    datasets version > dataset_cli_version.txt
    datasets summary genome accession "ESCAPED_$assembly" --as-json-lines > assembly_summary.jsonl
    rm -f dataset.zip
    datasets download genome accession "ESCAPED_$assembly" \
      --include genome,protein,gff3 \
      --no-progressbar \
      --filename dataset.zip
    test -s dataset.zip
    mkdir dataset
    sha256sum dataset.zip > dataset/dataset_sha256.txt
    cp dataset_cli_version.txt dataset/
    cp assembly_summary.jsonl dataset/
    unzip -q dataset.zip -d dataset
    test -s dataset/ncbi_dataset/data/assembly_data_report.jsonl
    fasta=ESCAPED_$(find dataset/ncbi_dataset/data -name '*_genomic.fna' -type f -print -quit)
    protein=ESCAPED_$(find dataset/ncbi_dataset/data -name 'protein.faa' -type f -print -quit)
    gff=ESCAPED_$(find dataset/ncbi_dataset/data -name 'genomic.gff' -type f -print -quit)
    for file in "ESCAPED_$fasta" "ESCAPED_$protein" "ESCAPED_$gff"; do
      if [[ -z "ESCAPED_$file" || ! -s "ESCAPED_$file" ]]; then
        echo "Missing or empty required NCBI annotation file: ESCAPED_$file" >&2
        exit 2
      fi
    done
    echo "Resolved nucleotide FASTA: ESCAPED_$fasta"
    echo "Resolved protein FASTA: ESCAPED_$protein"
    echo "Resolved GFF3 annotation: ESCAPED_$gff"
    """
    stub:
    """
    mkdir -p dataset/ncbi_dataset/data
    touch dataset/stub
    """
}

process AMRFINDERPLUS {
    publishDir params.outdir, mode: "copy", overwrite: true
    input:
    path dataset
    output:
    path "amrfinderplus_nucleotide_baseline.tsv"
    path "amrfinderplus_combined.tsv"
    path "amrfinderplus_summary.md"
    path "amrfinderplus_evidence.json"
    path "experiment_report.json"
    path "experiment_report.md"
    path "tool_versions.txt"
    path "amrfinderplus.log"
    path "dataset_cli_version.txt"
    path "dataset_sha256.txt"
    path "assembly_summary.jsonl"
    script:
    """
    set -Eeuo pipefail
    if [ -n "ESCAPED_${MAMBA_ROOT_PREFIX:-}" ] && [ -d "ESCAPED_$MAMBA_ROOT_PREFIX/envs/biosignal/bin" ]; then
      export PATH="ESCAPED_$MAMBA_ROOT_PREFIX/envs/biosignal/bin:ESCAPED_$PATH"
      export CONDA_PREFIX="ESCAPED_$MAMBA_ROOT_PREFIX/envs/biosignal"
    fi
    command -v amrfinder
    {
      echo "AMRFinderPlus executable: ESCAPED_$(command -v amrfinder)"
      amrfinder --version
      amrfinder --database_version
    } > tool_versions.txt 2>&1
    {
      echo "AMRFinderPlus diagnostics"
      echo "Working directory: ESCAPED_$PWD"
      echo "Executable: ESCAPED_$(command -v amrfinder)"
      cat tool_versions.txt
      echo "Staged input files:"
      find -L . -maxdepth 7 -type f -print | sort
    } > amrfinderplus.log 2>&1

    fasta=ESCAPED_$(find -L . -type f -name '*_genomic.fna' -print -quit)
    protein=ESCAPED_$(find -L . -type f -name 'protein.faa' -print -quit)
    gff=ESCAPED_$(find -L . -type f -name 'genomic.gff' -print -quit)
    for file in "ESCAPED_$fasta" "ESCAPED_$protein" "ESCAPED_$gff"; do
      if [[ -z "ESCAPED_$file" || ! -s "ESCAPED_$file" ]]; then
        echo "ERROR: Missing or empty combined-analysis input: ESCAPED_$file" | tee -a amrfinderplus.log >&2
        exit 2
      fi
    done

    echo "Validating NCBI FASTA/GFF identifier relationships" | tee -a amrfinderplus.log
    "${params.python_executable}" -m biosignal.amrfinder_report validate-inputs \
      --nucleotide "ESCAPED_$fasta" --protein "ESCAPED_$protein" --gff "ESCAPED_$gff" \
      >> amrfinderplus.log 2>&1

    {
      echo "Running nucleotide-only baseline"
      echo "Command: amrfinder --plus -n <genome.fna> -O ${params.amrfinder_organism} --print_node"
    } >> amrfinderplus.log
    amrfinder --plus -n "ESCAPED_$fasta" -O "${params.amrfinder_organism}" --print_node \
      -o amrfinderplus_nucleotide_baseline.tsv >> amrfinderplus.log 2>&1

    {
      echo "Running combined nucleotide + protein + GFF analysis"
      echo "Command: amrfinder --plus -n <genome.fna> -p <protein.faa> -g <genomic.gff> -O ${params.amrfinder_organism} --print_node"
    } >> amrfinderplus.log
    amrfinder --plus -n "ESCAPED_$fasta" -p "ESCAPED_$protein" -g "ESCAPED_$gff" \
      -O "${params.amrfinder_organism}" --print_node \
      -o amrfinderplus_combined.tsv >> amrfinderplus.log 2>&1

    test -s amrfinderplus_nucleotide_baseline.tsv
    test -s amrfinderplus_combined.tsv
    "${params.python_executable}" -m biosignal.amrfinder_report summarize \
      --report amrfinderplus_combined.tsv --output amrfinderplus_summary.md \
      >> amrfinderplus.log 2>&1
    test -s amrfinderplus_summary.md
    "${params.python_executable}" -m biosignal.amrfinder_report export-evidence \
      --report amrfinderplus_combined.tsv --output amrfinderplus_evidence.json \
      >> amrfinderplus.log 2>&1
    test -s amrfinderplus_evidence.json

    "${params.python_executable}" -m biosignal.amrfinder_report build-experiment-report \
      --evidence amrfinderplus_evidence.json \
      --isolate-id "${params.biosample}" \
      --organism "${params.report_organism}" \
      --source "NCBI BioSample / AMRFinderPlus public-isolate workflow" \
      --output-json experiment_report.json \
      --output-markdown experiment_report.md \
      >> amrfinderplus.log 2>&1
    test -s experiment_report.json
    test -s experiment_report.md

    cp "ESCAPED_$(find -L . -type f -name dataset_cli_version.txt -print -quit)" dataset_cli_version.txt
    cp "ESCAPED_$(find -L . -type f -name dataset_sha256.txt -print -quit)" dataset_sha256.txt
    cp "ESCAPED_$(find -L . -type f -name assembly_summary.jsonl -print -quit)" assembly_summary.jsonl
    {
      echo "Nucleotide baseline data rows: ESCAPED_$(awk 'END { print (NR > 0 ? NR - 1 : 0) }' amrfinderplus_nucleotide_baseline.tsv)"
      echo "Combined data rows: ESCAPED_$(awk 'END { print (NR > 0 ? NR - 1 : 0) }' amrfinderplus_combined.tsv)"
      echo "Combined summary:"
      cat amrfinderplus_summary.md
      echo "Unified experiment report:"
      cat experiment_report.md
    } >> amrfinderplus.log
    """
    stub:
    """
    printf "Element symbol\\tScope\\tType\\tMethod\\n" > amrfinderplus_nucleotide_baseline.tsv
    printf "Element symbol\\tScope\\tType\\tMethod\\n" > amrfinderplus_combined.tsv
    echo "# Stub only — no biological analysis was performed." > amrfinderplus_summary.md
    echo '{"schema_version":"1.0","source":"AMRFinderPlus","row_count":0,"amr_typed_rows":0,"scope_counts":{},"type_counts":{},"review_flag_rows":0,"detections":[],"interpretation":"Stub only; no biological analysis was performed."}' > amrfinderplus_evidence.json
    echo '{"schema_version":"1.0","report_type":"research_evidence_summary","isolate_id":"STUB","organism":"STUB","source":"Nextflow stub","amr_hits":[],"genomic_detections":[],"comparisons":[],"limitations":["Stub only — no biological analysis was performed"],"interpretation":"Stub only — no biological analysis was performed."}' > experiment_report.json
    echo "# Stub only — no biological analysis was performed." > experiment_report.md
    echo "stub" > tool_versions.txt
    echo "stub" > amrfinderplus.log
    echo "stub" > dataset_cli_version.txt
    echo "stub" > dataset_sha256.txt
    echo "stub" > assembly_summary.jsonl
    """
}

workflow {
    assembly = RESOLVE_ASSEMBLY(params.biosample)
    genome = DOWNLOAD_GENOME(assembly)
    AMRFINDERPLUS(genome)
}
