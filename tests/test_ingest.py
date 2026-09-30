from pathlib import Path

from biosignal.ingest import load_csv


def test_load_csv():
    path = Path("data/examples/amr_observations.csv")
    observations = load_csv(path)

    assert len(observations) == 4
    assert observations[0].organism == "Escherichia coli"
    assert observations[1].resistance_rate == 0.35
