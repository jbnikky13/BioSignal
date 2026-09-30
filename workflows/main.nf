nextflow.enable.dsl=2

/*
 BioSignal reproducible workflow skeleton.
 Tool/reference versions should be pinned before production runs.
*/
params.input = null

process AMRFINDERPLUS {
    tag "$sample_id"
    input:
    tuple val(sample_id), path(fasta)
    output:
    tuple val(sample_id), path("amrfinderplus.tsv"), emit: amr
    script:
    """
    amrfinder -n ${fasta} -o amrfinderplus.tsv
    """
}

workflow {
    if (!params.input) {
        error "Provide --input with a FASTA file"
    }
    samples = channel.fromPath(params.input, checkIfExists: true)
        .map { file -> tuple(file.baseName, file) }
    AMRFINDERPLUS(samples)
}
