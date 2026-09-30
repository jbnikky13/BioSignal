"""Small, strict GFF3 parser for NCBI genome annotations."""
from dataclasses import dataclass


@dataclass(frozen=True)
class GFF3Feature:
    seqid: str
    source: str
    feature_type: str
    start: int
    end: int
    strand: str
    attributes: dict[str, str]


def parse_attributes(raw: str) -> dict[str, str]:
    result: dict[str, str] = {}
    if raw == ".":
        return result
    for item in raw.split(";"):
        if not item:
            continue
        if "=" in item:
            key, value = item.split("=", 1)
            result[key] = value
    return result


def read_gff3(text: str) -> list[GFF3Feature]:
    features: list[GFF3Feature] = []
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        fields = line.split("\t")
        if len(fields) != 9:
            raise ValueError("GFF3 feature must contain 9 tab-separated columns")
        start, end = int(fields[3]), int(fields[4])
        if start < 1 or end < start:
            raise ValueError("invalid GFF3 coordinates")
        features.append(GFF3Feature(
            seqid=fields[0],
            source=fields[1],
            feature_type=fields[2],
            start=start,
            end=end,
            strand=fields[6],
            attributes=parse_attributes(fields[8]),
        ))
    return features
