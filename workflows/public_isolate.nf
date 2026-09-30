nextflow.enable.dsl=2

params.biosample = "SAMN05170351"
params.outdir = "results"

process RESOLVE_ASSEMBLY {
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
    assembly = meta.assembly_accession
    """
    datasets download genome accession ${assembly} --include genome,gff3 --filename dataset.zip
    mkdir dataset
    unzip -q dataset.zip -d dataset
    """
}

process AMRFINDERPLUS {
    input:
    path dataset
    output:
    path "amrfinderplus.tsv"
    path "tool_versions.txt"
    script:
    """
    fasta=$(find dataset -name '*_genomic.fna' -type f | head -1)
    test -n "\$fasta"
    amrfinder --version > tool_versions.txt
    amrfinder -n "\$fasta" -o amrfinderplus.tsv
    """
}

workflow {
    assembly_manifest = RESOLVE_ASSEMBLY(params.biosample)
    genome = DOWNLOAD_GENOME(assembly_manifest)
    AMRFINDERPLUS(genome)
}
