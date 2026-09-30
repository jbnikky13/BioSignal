from biosignal.taxonomy import normalize_taxon

def test_known_alias_resolves_to_ncbi_taxid():
    result = normalize_taxon("E. coli")
    assert result.scientific_name == "Escherichia coli"
    assert result.taxid == 562
    assert result.status == "resolved"

def test_unknown_name_is_not_guessed():
    result = normalize_taxon("Unknown organism")
    assert result.status == "unresolved"
    assert result.taxid is None