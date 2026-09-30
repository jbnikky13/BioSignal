from biosignal.amr import parse_amrfinder_rows


def test_normalizes_amrfinder_result():
    hits = parse_amrfinder_rows([{
        "Protein identifier": "WP_001",
        "Element symbol": "blaX",
        "Type": "AMR",
        "Method": "BLAST",
        "Reference sequence accession": "WP_REF",
        "% Coverage of reference sequence": "98.5",
        "% Identity to reference sequence": "99.1",
    }])
    assert hits[0].gene_symbol == "blaX"
    assert hits[0].coverage == 98.5
    assert hits[0].identity == 99.1
