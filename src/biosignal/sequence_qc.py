"""Lightweight QC metrics for FASTA/FASTQ-like sequence records.

This layer intentionally operates on sequence records already obtained through
an approved/public data source. It does not make clinical or resistance claims.
"""
from dataclasses import dataclass
from collections.abc import Iterable


@dataclass(frozen=True)
class SequenceQC:
    sequence_id: str
    length: int
    gc_fraction: float
    ambiguous_bases: int
    n_fraction: float
    status: str
    warnings: tuple[str, ...]


def assess_sequence(sequence_id: str, sequence: str, *, min_length: int = 500) -> SequenceQC:
    seq = "".join(sequence.split()).upper()
    if not seq:
        raise ValueError("sequence must not be empty")

    length = len(seq)
    ambiguous = sum(base not in {"A", "C", "G", "T"} for base in seq)
    gc = (seq.count("G") + seq.count("C")) / length
    n_fraction = seq.count("N") / length

    warnings: list[str] = []
    if length < min_length:
        warnings.append("short sequence")
    if n_fraction > 0.01:
        warnings.append("high N fraction")
    if ambiguous > seq.count("N"):
        warnings.append("non-IUPAC base characters")

    status = "pass" if not warnings else "review"
    return SequenceQC(
        sequence_id=sequence_id,
        length=length,
        gc_fraction=round(gc, 4),
        ambiguous_bases=ambiguous,
        n_fraction=round(n_fraction, 4),
        status=status,
        warnings=tuple(warnings),
    )


def assess_fasta(records: Iterable[tuple[str, str]], *, min_length: int = 500) -> list[SequenceQC]:
    return [assess_sequence(sequence_id, sequence, min_length=min_length) for sequence_id, sequence in records]
