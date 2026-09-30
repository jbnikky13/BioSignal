"""Minimal FASTA parser used by the BioSignal QC layer."""
from collections.abc import Iterator


def read_fasta(text: str) -> Iterator[tuple[str, str]]:
    current_id: str | None = None
    chunks: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if current_id is not None:
                yield current_id, "".join(chunks)
            current_id = line[1:].split()[0]
            chunks = []
        else:
            if current_id is None:
                raise ValueError("FASTA sequence appears before a header")
            chunks.append(line)

    if current_id is not None:
        yield current_id, "".join(chunks)
