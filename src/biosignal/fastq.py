"""Minimal FASTQ parser with structural validation."""

from collections.abc import Iterator


def read_fastq(text: str) -> Iterator[tuple[str, str, str]]:
    """Yield (read_id, sequence, quality) records.

    FASTQ records are four lines: header, sequence, '+', quality.
    Wrapped/multiline FASTQ is intentionally rejected so malformed input
    cannot silently enter downstream analysis.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) % 4:
        raise ValueError("FASTQ input must contain complete four-line records")

    for i in range(0, len(lines), 4):
        header, sequence, plus, quality = lines[i:i + 4]
        if not header.startswith("@"):
            raise ValueError("FASTQ header must start with '@'")
        if plus != "+":
            raise ValueError("FASTQ separator line must be '+'")
        if len(sequence) != len(quality):
            raise ValueError("sequence and quality lengths must match")
        yield header[1:].split()[0], sequence.upper(), quality


def phred33_scores(quality: str) -> list[int]:
    """Convert standard Phred+33 quality characters to integer scores."""
    return [ord(char) - 33 for char in quality]
