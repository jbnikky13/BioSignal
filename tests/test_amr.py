from biosignal.amr import parse_amrfinder_rows


def test_parses_current_combined_amrfinder_headers_and_preserves_scope():
    hits = parse_amrfinder_rows([{
        "Protein id": "WP_001",
        "Contig id": "CP000001.1",
        "Start": "10",
        "Stop": "900",
        "Element symbol": "blaX",
        "Element name": "beta-lactamase",
        "Scope": "plus",
        "Type": "AMR",
        "Method": "BLASTP",
        "Closest reference accession": "WP_REF",
        "% Coverage of reference": "98.5",
        "% Identity to reference": "99.1",
    }])
    hit = hits[0]
    assert hit.gene_symbol == "blaX"
    assert hit.scope == "plus"
    assert hit.element_type == "AMR"
    assert hit.reference == "WP_REF"
    assert hit.coverage == 98.5
    assert hit.identity == 99.1
    assert hit.contig_id == "CP000001.1"
    assert hit.is_amr_typed


def test_parses_legacy_headers_without_inventing_scope():
    hit = parse_amrfinder_rows([{
        "Protein identifier": "WP_001",
        "Element symbol": "blaX",
        "Type": "AMR",
        "Method": "BLAST",
        "Reference sequence accession": "WP_REF",
        "% Coverage of reference sequence": "98.5",
        "% Identity to reference sequence": "99.1",
    }])[0]
    assert hit.scope == "unknown"
    assert hit.coverage == 98.5
    assert hit.identity == 99.1


def test_internal_stop_is_retained_as_manual_review_flag():
    hit = parse_amrfinder_rows([{
        "Protein id": "WP_002",
        "Contig id": "contig1",
        "Element symbol": "espX1",
        "Scope": "plus",
        "Type": "VIRULENCE",
        "Method": "INTERNAL_STOP",
    }])[0]
    assert hit.review_required is True
    assert hit.review_reasons == ("INTERNAL_STOP",)
    assert not hit.is_amr_typed


def test_na_numeric_metrics_are_preserved_as_missing_values():
    hit = parse_amrfinder_rows([{
        "Protein id": "WP_003",
        "Contig id": "contig1",
        "Start": "NA",
        "Stop": "N/A",
        "Element symbol": "geneX",
        "Scope": "plus",
        "Type": "VIRULENCE",
        "Method": "BLASTP",
        "% Coverage of reference": "NA",
        "% Identity to reference": ".",
        "Closest reference accession": "NA",
    }])[0]
    assert hit.coverage is None
    assert hit.identity is None
    assert hit.start is None
    assert hit.stop is None
    assert hit.reference is None


def test_numeric_metrics_still_parse_when_present():
    hit = parse_amrfinder_rows([{
        "% Coverage of reference": "100",
        "% Identity to reference": "99.75",
        "Start": "12",
        "Stop": "345",
    }])[0]
    assert hit.coverage == 100.0
    assert hit.identity == 99.75
    assert hit.start == 12
    assert hit.stop == 345
