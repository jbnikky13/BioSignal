from pathlib import Path
from biosignal.execution import AssemblyManifest, build_manifest_from_assembly, write_manifest

def test_builds_and_writes_assembly_manifest(tmp_path: Path):
    assembly = type("Assembly", (), {
        "assembly_accession": "GCA_123456.1",
        "assembly_name": "ASM123",
        "assembly_level": "Complete Genome",
        "organism": "Escherichia coli",
    })()
    manifest = build_manifest_from_assembly(assembly, "SAMN05170351")
    path = write_manifest(manifest, tmp_path / "manifest.json")
    assert manifest.assembly_accession == "GCA_123456.1"
    assert path.exists()
    assert "SAMN05170351" in path.read_text()
