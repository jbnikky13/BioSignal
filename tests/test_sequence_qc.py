from biosignal.sequence_qc import assess_sequence


def test_sequence_qc_calculates_basic_metrics():
    qc = assess_sequence("contig-1", "ACGT" * 200)
    assert qc.length == 800
    assert qc.gc_fraction == 0.5
    assert qc.ambiguous_bases == 0
    assert qc.status == "pass"


def test_sequence_qc_flags_short_sequence_and_ns():
    qc = assess_sequence("contig-2", "ACGTNN" * 20, min_length=500)
    assert qc.status == "review"
    assert "short sequence" in qc.warnings
    assert "high N fraction" in qc.warnings


def test_empty_sequence_is_rejected():
    try:
        assess_sequence("empty", "")
    except ValueError as exc:
        assert "empty" in str(exc)
    else:
        raise AssertionError("expected ValueError")
