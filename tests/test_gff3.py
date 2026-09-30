from biosignal.gff3 import parse_attributes, read_gff3


def test_parses_gff3_feature():
    text = "NC_1\tRefSeq\tCDS\t10\t100\t.\t+\t0\tID=cds1;gene=blaX;product=test"
    features = read_gff3(text)
    assert features[0].feature_type == "CDS"
    assert features[0].start == 10
    assert features[0].attributes["gene"] == "blaX"


def test_invalid_column_count_is_rejected():
    try:
        read_gff3("NC_1\tRefSeq\tCDS\t10")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")


def test_attribute_parser():
    assert parse_attributes("ID=x;Parent=y") == {"ID": "x", "Parent": "y"}
