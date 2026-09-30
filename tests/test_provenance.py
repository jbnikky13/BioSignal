from biosignal.provenance import DatasetProvenance


def test_provenance_records_source():
    record = DatasetProvenance.now(
        source_name="WHO GLASS-AMR",
        endpoint="https://example.org/amr",
        row_count=42,
    )
    assert record.source_name == "WHO GLASS-AMR"
    assert record.row_count == 42
    assert record.retrieved_at.tzinfo is not None
