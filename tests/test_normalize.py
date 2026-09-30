from biosignal.normalize import normalize_row

def test_normalizes_explicitly_mapped_row():
    row = {
        "PERIOD_START": "2026-01-01",
        "PERIOD_END": "2026-03-31",
        "TESTED_COUNT": "100",
        "RESISTANT_COUNT": "25",
    }
    obs = normalize_row(
        row,
        organism="Escherichia coli",
        antimicrobial="ciprofloxacin",
        region="Nigeria",
    )
    assert obs.organism == "Escherichia coli"
    assert obs.antimicrobial == "ciprofloxacin"
    assert obs.resistance_rate == 0.25
    assert obs.source == "WHO GLASS-AMR"
