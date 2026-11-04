nextflow.enable.dsl=2

params.biosample = "SAMN05215988"
params.amrfinder_organism = "Escherichia"
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
    assembly=\$(tr -d '[:space:]' < ${assembly_accession_file})
    test -n "\$assembly"
    if [[ ! "\$assembly" =~ ^(GCA|GCF)_[0-9]+\\.[0-9]+\$ ]]; then
      echo "Invalid NCBI assembly accession: \$assembly" >&2
      exit 1
    fi
    echo "Downloading NCBI assembly with genome, protein and GFF3: \$assembly"
    datasets version > dataset_cli_version.txt
    datasets summary genome accession "\$assembly" --as-json-lines > assembly_summary.jsonl
    rm -f dataset.zip
    datasets download genome accession "\$assembly" \
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
    fasta=\$(find dataset/ncbi_dataset/data -name '*_genomic.fna' -type f -print -quit)
    protein=\$(find dataset/ncbi_dataset/data -name 'protein.faa' -type f -print -quit)
    gff=\$(find dataset/ncbi_dataset/data -name 'genomic.gff' -type f -print -quit)
    for file in "\$fasta" "\$protein" "\$gff"; do
      if [[ -z "\$file" || ! -s "\$file" ]]; then
        echo "Missing or empty required NCBI annotation file: \$file" >&2
        exit 2
      fi
    done
    echo "Resolved nucleotide FASTA: \$fasta"
    echo "Resolved protein FASTA: \$protein"
    echo "Resolved GFF3 annotation: \$gff"
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
    path "tool_versions.txt"
    path "amrfinderplus.log"
    path "dataset_cli_version.txt"
    path "dataset_sha256.txt"
    path "assembly_summary.jsonl"
    script:
    """
    set -Eeuo pipefail
    if [ -n "\${MAMBA_ROOT_PREFIX:-}" ] && [ -d "\$MAMBA_ROOT_PREFIX/envs/biosignal/bin" ]; then
      export PATH="\$MAMBA_ROOT_PREFIX/envs/biosignal/bin:\$PATH"
      export CONDA_PREFIX="\$MAMBA_ROOT_PREFIX/envs/biosignal"
    fi
    command -v amrfinder
    {
      echo "AMRFinderPlus executable: \$(command -v amrfinder)"
      amrfinder --version
      amrfinder --database_version
    } > tool_versions.txt 2>&1
    {
      echo "AMRFinderPlus diagnostics"
      echo "Working directory: \$PWD"
      echo "Executable: \$(command -v amrfinder)"
      cat tool_versions.txt
      echo "Staged input files:"
      find -L . -maxdepth 7 -type f -print | sort
    } > amrfinderplus.log 2>&1

    fasta=\$(find -L . -type f -name '*_genomic.fna' -print -quit)
    protein=\$(find -L . -type f -name 'protein.faa' -print -quit)
    gff=\$(find -L . -type f -name 'genomic.gff' -print -quit)
    for file in "\$fasta" "\$protein" "\$gff"; do
      if [[ -z "\$file" || ! -s "\$file" ]]; then
        echo "ERROR: Missing or empty combined-analysis input: \$file" | tee -a amrfinderplus.log >&2
        exit 2
      fi
    done

    echo "Validating NCBI FASTA/GFF identifier relationships" | tee -a amrfinderplus.log
    "${params.python_executable}" -m biosignal.amrfinder_report validate-inputs \
      --nucleotide "\$fasta" --protein "\$protein" --gff "\$gff" \
      >> amrfinderplus.log 2>&1

    {
      echo "Running nucleotide-only baseline"
      echo "Command: amrfinder --plus -n <genome.fna> -O ${params.amrfinder_organism} --print_node"
    } >> amrfinderplus.log
    amrfinder --plus -n "\$fasta" -O "${params.amrfinder_organism}" --print_node \
      -o amrfinderplus_nucleotide_baseline.tsv >> amrfinderplus.log 2>&1

    {
      echo "Running combined nucleotide + protein + GFF analysis"
      echo "Command: amrfinder --plus -n <genome.fna> -p <protein.faa> -g <genomic.gff> -O ${params.amrfinder_organism} --print_node"
    } >> amrfinderplus.log
    amrfinder --plus -n "\$fasta" -p "\$protein" -g "\$gff" \
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
    cp "\$(find -L . -type f -name dataset_cli_version.txt -print -quit)" dataset_cli_version.txt
    cp "\$(find -L . -type f -name dataset_sha256.txt -print -quit)" dataset_sha256.txt
    cp "\$(find -L . -type f -name assembly_summary.jsonl -print -quit)" assembly_summary.jsonl
    {
      echo "Nucleotide baseline data rows: \$(awk 'END { print (NR > 0 ? NR - 1 : 0) }' amrfinderplus_nucleotide_baseline.tsv)"
      echo "Combined data rows: \$(awk 'END { print (NR > 0 ? NR - 1 : 0) }' amrfinderplus_combined.tsv)"
      echo "Combined summary:"
      cat amrfinderplus_summary.md
    } >> amrfinderplus.log
    """
    stub:
    """
    printf "Element symbol\\tScope\\tType\\tMethod\\n" > amrfinderplus_nucleotide_baseline.tsv
    printf "Element symbol\\tScope\\tType\\tMethod\\n" > amrfinderplus_combined.tsv
    echo "# Stub only — no biological analysis was performed." > amrfinderplus_summary.md
    echo '{"schema_version":"1.0","source":"AMRFinderPlus","row_count":0,"amr_typed_rows":0,"scope_counts":{},"type_counts":{},"review_flag_rows":0,"detections":[],"interpretation":"Stub only; no biological analysis was performed."}' > amrfinderplus_evidence.json
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
