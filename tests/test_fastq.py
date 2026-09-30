from biosignal.fastq import phred33_scores, read_fastq


def test_reads_fastq_record():
    records = list(read_fastq("@read1\nACGT\n+\nIIII\n"))
    assert records == [("read1", "ACGT", "IIII")]


def test_quality_scores_use_phred33():
    assert phred33_scores("IIII") == [40, 40, 40, 40]


def test_rejects_length_mismatch():
    try:
        list(read_fastq("@read1\nACGT\n+\nIII\n"))
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")
