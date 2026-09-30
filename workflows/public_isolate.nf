nextflow.enable.dsl=2

params.biosample = "SAMN05215988"
params.amrfinder_organism = "Escherichia"
params.outdir = "results"

process RESOLVE_ASSEMBLY {
    publishDir params.outdir, mode: "copy", overwrite: true
    output:
    tuple path("assembly_manifest.json"), path("assembly_accession.txt")
    script:
    """
    python -m biosignal.resolve_assembly ${params.biosample} --output assembly_manifest.json
    python -c 'import json; print(json.load(open("assembly_manifest.json", encoding="utf-8"))["assembly_accession"])' > assembly_accession.txt
    """
    stub:
    """
    echo '{"biosample_accession":"${params.biosample}","assembly_accession":"GCA_STUB.1"}' > assembly_manifest.json
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
    fasta=\$(find dataset -name '*_genomic.fna' -type f | head -1)
    gff=\$(find dataset -type f -name '*.gff*' | head -1)
    test -s "\$fasta"

    amrfinder --database_version > tool_versions.txt 2>&1

    # AMRFinderPlus reliably supports assembly-level nucleotide screening.
    # Use the NCBI GFF only as an optional annotation input; a malformed or
    # incompatible GFF must not prevent the core AMR screen from running.
    if [ -n "\$gff" ] && [ -s "\$gff" ]; then
      echo "FASTA: \$fasta" > amrfinderplus.log
      echo "GFF: \$gff" >> amrfinderplus.log
      amrfinder --plus --organism ${params.amrfinder_organism} -n "\$fasta" -g "\$gff" --print_node -o amrfinderplus.tsv >> amrfinderplus.log 2>&1
      status=\$?
      if [ "\$status" -ne 0 ]; then
        echo "Combined nucleotide+GFF AMRFinder run failed (exit \$status); retrying with nucleotide-only screening." >> amrfinderplus.log
        amrfinder --plus --organism ${params.amrfinder_organism} -n "\$fasta" --print_node -o amrfinderplus.tsv >> amrfinderplus.log 2>&1
      fi
    else
      echo "No usable GFF found; running nucleotide-only AMRFinder screening." > amrfinderplus.log
      amrfinder --plus --organism ${params.amrfinder_organism} -n "\$fasta" --print_node -o amrfinderplus.tsv >> amrfinderplus.log 2>&1
    fi

    test -s amrfinderplus.tsv
    """
    stub:
    """
    echo "stub" > amrfinderplus.tsv
    echo "stub" > tool_versions.txt
    echo "stub" > amrfinderplus.log
    """
}

workflow {
    assembly = RESOLVE_ASSEMBLY()
    genome = DOWNLOAD_GENOME(assembly)
    AMRFINDERPLUS(genome)
}
