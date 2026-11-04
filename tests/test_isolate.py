from biosignal.isolate import canonical_isolate_id, harmonize_amr_evidence


def test_prefers_biosample_as_stable_isolate_identity():
    assert canonical_isolate_id({"BioSample": "SAMN123"}) == "SAMN123"


def test_harmonizes_current_amrfinder_headers_scope_and_metrics():
    evidence = harmonize_amr_evidence("SAMN123", [{
        "Element symbol": "blaKPC-2",
        "Type": "AMR",
        "Scope": "core",
        "Method": "BLASTP",
        "% Identity to reference": "99.2",
        "% Coverage of reference": "98.1",
        "Closest reference accession": "WP_REF",
        "Contig id": "contig1",
        "Start": "100",
        "Stop": "900",
        "Database version": "2026-10-29.1",
    }])[0]
    assert evidence.gene_symbol == "blaKPC-2"
    assert evidence.identity == 99.2
    assert evidence.coverage == 98.1
    assert evidence.scope == "core"
    assert evidence.reference == "WP_REF"
    assert evidence.analysis_version is None
    assert evidence.reference_catalog_version == "2026-10-29.1"


def test_harmonizes_plus_virulence_and_internal_stop_without_calling_it_amr():
    evidence = harmonize_amr_evidence("SAMN123", [{
        "Element symbol": "espX1",
        "Type": "VIRULENCE",
        "Scope": "plus",
        "Method": "INTERNAL_STOP",
    }])[0]
    assert evidence.scope == "plus"
    assert evidence.evidence_type == "VIRULENCE"
    assert evidence.review_required is True
    assert evidence.review_reasons == ("INTERNAL_STOP",)
