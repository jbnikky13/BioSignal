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



def test_normalizes_optional_comparability_metadata():
    row = {
        "PERIOD_START": "2026-01-01",
        "PERIOD_END": "2026-03-31",
        "TESTED_COUNT": "100",
        "RESISTANT_COUNT": "25",
        "SPECIMEN_TYPE": " urine ",
        "TESTING_CRITERIA": "EUCAST 2025",
        "LABORATORY_METHOD": "disk diffusion",
    }

    obs = normalize_row(
        row,
        organism="Escherichia coli",
        antimicrobial="ciprofloxacin",
    )

    assert obs.specimen_type == "urine"
    assert obs.testing_criteria == "EUCAST 2025"
    assert obs.laboratory_method == "disk diffusion"


def test_normalization_keeps_absent_comparability_metadata_unknown():
    row = {
        "PERIOD_START": "2026-01-01",
        "PERIOD_END": "2026-03-31",
        "TESTED_COUNT": "100",
        "RESISTANT_COUNT": "25",
        "SPECIMEN_TYPE": " ",
    }

    obs = normalize_row(
        row,
        organism="Escherichia coli",
        antimicrobial="ciprofloxacin",
    )

    assert obs.specimen_type is None
    assert obs.testing_criteria is None
    assert obs.laboratory_method is None
