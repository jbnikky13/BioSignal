from pathlib import Path

from biosignal.ingest import load_csv


def test_load_csv():
    path = Path("data/examples/amr_observations.csv")
    observations = load_csv(path)

    assert len(observations) == 4
    assert observations[0].organism == "Escherichia coli"
    assert observations[1].resistance_rate == 0.35



def test_load_csv_preserves_optional_comparability_metadata(tmp_path):
    path = tmp_path / "observations.csv"
    path.write_text(
        "organism,antimicrobial,period_start,period_end,tested_count,resistant_count,region,source,specimen_type,testing_criteria,laboratory_method\n"
        "E. coli,ciprofloxacin,2026-01-01,2026-03-31,100,25,north,lab-a,urine,EUCAST 2025,disk diffusion\n",
        encoding="utf-8",
    )

    observation = load_csv(path)[0]

    assert observation.specimen_type == "urine"
    assert observation.testing_criteria == "EUCAST 2025"
    assert observation.laboratory_method == "disk diffusion"


def test_load_csv_defaults_missing_comparability_metadata_to_none(tmp_path):
    path = tmp_path / "observations.csv"
    path.write_text(
        "organism,antimicrobial,period_start,period_end,tested_count,resistant_count\n"
        "E. coli,ciprofloxacin,2026-01-01,2026-03-31,100,25\n",
        encoding="utf-8",
    )

    observation = load_csv(path)[0]

    assert observation.specimen_type is None
    assert observation.testing_criteria is None
    assert observation.laboratory_method is None
