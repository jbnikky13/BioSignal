from biosignal.fasta import read_fasta


def test_reads_multiline_fasta():
    records = list(read_fasta(">seq1 description\nACGTAC\nGT\n>seq2\nNNNN\n"))
    assert records == [("seq1", "ACGTACGT"), ("seq2", "NNNN")]


def test_rejects_sequence_before_header():
    try:
        list(read_fasta("ACGT"))
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")
