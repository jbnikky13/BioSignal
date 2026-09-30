"""CLI for resolving an NCBI BioSample accession to a reviewable assembly manifest."""

from __future__ import annotations

import argparse

from .execution import build_manifest_from_assembly, write_manifest
from .ncbi_genome import find_assemblies_by_biosample


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("biosample")
    parser.add_argument(
        "--output",
        default="data/public/assembly_manifest.json",
    )
    args = parser.parse_args()

    assemblies = find_assemblies_by_biosample(args.biosample)
    if not assemblies:
        raise SystemExit(f"No public assembly found for {args.biosample}")

    manifest = build_manifest_from_assembly(assemblies[0], args.biosample)
    path = write_manifest(manifest, args.output)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
