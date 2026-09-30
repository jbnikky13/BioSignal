from biosignal.fetch import parse_csv


def test_parse_csv_response():
    rows = parse_csv("organism,tested_count\nE. coli,10\n")
    assert rows == [{"organism": "E. coli", "tested_count": "10"}]
