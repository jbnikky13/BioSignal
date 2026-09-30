from biosignal.isolate import canonical_isolate_id, harmonize_amr_evidence

def test_prefers_biosample_as_stable_isolate_identity():
    assert canonical_isolate_id({"BioSample": "SAMN123"}) == "SAMN123"

def test_harmonizes_amr_versions_and_metrics():
    evidence = harmonize_amr_evidence("SAMN123", [{"Element symbol": "blaKPC-2", "Type": "AMR", "Method": "BLASTP", "% Identity": "99.2", "% Coverage": "98.1", "AMRFinderPlus version": "4.0.22", "PD Ref Gene Catalog Version": "2026-01-01.1"}])
    assert evidence[0].gene_symbol == "blaKPC-2"
    assert evidence[0].identity == 99.2
    assert evidence[0].analysis_version == "4.0.22"
