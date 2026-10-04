nextflow.enable.dsl=2

params.biosample = "SAMN05215988"
params.amrfinder_organism = "Escherichia"
params.outdir = "results"

process RESOLVE_ASSEMBLY {
    publishDir params.outdir, mode: "copy", overwrite: true
    input:
    val biosample
    output:
    tuple path("assembly_manifest.json"), path("assembly_accession.txt")
    script:
    """
    python -m biosignal.resolve_assembly "${biosample}" --output assembly_manifest.json
    python -c 'import json; print(json.load(open("assembly_manifest.json", encoding="utf-8"))["assembly_accession"])' > assembly_accession.txt
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
    assembly=\$(cat ${assembly_accession_file})
    test -n "\$assembly"
    datasets download genome accession "\$assembly" --include genome,gff3 --no-progressbar --filename dataset.zip
    mkdir dataset
    unzip -q dataset.zip -d dataset
    test -s dataset/ncbi_dataset/data/assembly_data_report.jsonl
    test -n "\$(find dataset -name '*_genomic.fna' -type f | head -1)"
    """
    stub:
    """
    mkdir -p dataset
    touch dataset/stub
    """
}

process AMRFINDERPLUS {
    publishDir params.outdir, mode: "copy", overwrite: true
    input:
    path dataset
    output:
    path "amrfinderplus.tsv"
    path "tool_versions.txt"
    path "amrfinderplus.log"
    script:
    """
    set -Eeuo pipefail

    fasta=\$(find dataset -name '*_genomic.fna' -type f -print -quit)
    test -n "\$fasta"
    test -s "\$fasta"

    {
      echo "AMRFinderPlus version:"
      amrfinder --database_version
      echo "FASTA: \$fasta"
    } > tool_versions.txt 2>&1

    {
      echo "AMRFinderPlus diagnostics"
      echo "FASTA: \$fasta"
      echo "--- command ---"
      echo "amrfinder --plus -n \$fasta -O ${params.amrfinder_organism} --print_node"
      echo "--- output ---"
    } > amrfinderplus.log

    set +e
    amrfinder --plus -n "\$fasta" -O ${params.amrfinder_organism} --print_node \
      -o amrfinderplus.tsv >> amrfinderplus.log 2>&1
    status=\$?
    set -e

    echo "AMRFinder exit status: \$status" >> amrfinderplus.log
    if [ "\$status" -ne 0 ]; then
      cat amrfinderplus.log >&2
      exit "\$status"
    fi

    test -s amrfinderplus.tsv
    printf "AMRFinder report rows: " >> amrfinderplus.log
    wc -l < amrfinderplus.tsv >> amrfinderplus.log
    """
    stub:
    """
    echo "stub" > amrfinderplus.tsv
    echo "stub" > tool_versions.txt
    echo "stub" > amrfinderplus.log
    """
}

workflow {
    assembly = RESOLVE_ASSEMBLY(params.biosample)
    genome = DOWNLOAD_GENOME(assembly)
    AMRFINDERPLUS(genome)
}
