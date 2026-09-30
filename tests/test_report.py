from biosignal.report import to_dict
from biosignal.signals import detect_amr_signal
from biosignal.models import AMRObservation
from datetime import date


def test_signal_report_is_serializable():
    obs = AMRObservation(
        organism="E. coli",
        antimicrobial="ciprofloxacin",
        period_start=date(2026, 1, 1),
        period_end=date(2026, 3, 31),
        tested_count=100,
        resistant_count=25,
    )
    report = to_dict(detect_amr_signal(obs))
    assert report["current_rate"] == 0.25
    assert report["severity"] == "watch"
