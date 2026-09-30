"""Genome/sequence feature extraction primitives."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SequenceFeatures:
    sequence_id: str
    length: int
    gc_fraction: float
    n_fraction: float
    kmer_counts: dict[str, int]


def extract_features(
    sequence_id: str,
    sequence: str,
    *,
    k: int = 3,
) -> SequenceFeatures:
    """Extract transparent sequence-level features.

    K-mers containing non-ACGT characters are skipped. This is a feature
    representation only; it does not identify genes or resistance.
    """
    if k < 1:
        raise ValueError("k must be >= 1")

    seq = "".join(sequence.split()).upper()
    if not seq:
        raise ValueError("sequence must not be empty")

    kmer_counts: dict[str, int] = {}
    for i in range(len(seq) - k + 1):
        kmer = seq[i:i + k]
        if all(base in "ACGT" for base in kmer):
            kmer_counts[kmer] = kmer_counts.get(kmer, 0) + 1

    gc = (seq.count("G") + seq.count("C")) / len(seq)
    return SequenceFeatures(
        sequence_id=sequence_id,
        length=len(seq),
        gc_fraction=round(gc, 4),
        n_fraction=round(seq.count("N") / len(seq), 4),
        kmer_counts=kmer_counts,
    )
