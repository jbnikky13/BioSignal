from biosignal.features import extract_features


def test_extracts_basic_features_and_kmers():
    result = extract_features("contig-1", "ACGTAC", k=2)
    assert result.length == 6
    assert result.gc_fraction == 0.5
    assert result.kmer_counts["AC"] == 2
    assert result.kmer_counts["CG"] == 1


def test_skips_kmers_with_ambiguous_bases():
    result = extract_features("contig-1", "ACNNGT", k=3)
    assert "ACN" not in result.kmer_counts
