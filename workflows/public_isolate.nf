nextflow.enable.dsl=2

params.biosample = "SAMN05170351"
params.amrfinder_organism = "Escherichia"
params.outdir = "results"

process RESOLVE_ASSEMBLY {
    publishDir params.outdir, mode: "copy", overwrite: true
    output:
    path "assembly_manifest.json"
    script:
    """
    python scripts/resolve_assembly.py ${params.biosample} --output assembly_manifest.json
    """
}

process DOWNLOAD_GENOME {
    input:
    path manifest
    output:
    path "dataset"
    script:
    def meta = new groovy.json.JsonSlurper().parse(manifest)
    def assembly = meta.assembly_accession
    """
    datasets download genome accession ${assembly} --include genome,gff3 --no-progressbar --filename dataset.zip
    mkdir dataset
    unzip -q dataset.zip -d dataset
    test -s dataset/ncbi_dataset/data/assembly_data_report.jsonl
    """
}

process AMRFINDERPLUS {
    publishDir params.outdir, mode: "copy", overwrite: true
    input:
    path dataset
    output:
    path "amrfinderplus.tsv"
    path "tool_versions.txt"
    script:
    """
    fasta=\$(find dataset -name '*_genomic.fna' -type f | head -1)
    gff=\$(find dataset -type f \( -name '*.gff' -o -name '*.gff3' \) | head -1)
    test -s "\$fasta"
    test -s "\$gff"
    amrfinder --database_version > tool_versions.txt
    amrfinder --plus --organism ${params.amrfinder_organism} -n "\$fasta" -g "\$gff" --print_node -o amrfinderplus.tsv
    test -s amrfinderplus.tsv
    """
}

workflow {
    assembly_manifest = RESOLVE_ASSEMBLY()
    genome = DOWNLOAD_GENOME(assembly_manifest)
    AMRFINDERPLUS(genome)
}