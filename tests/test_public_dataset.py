import os
import pytest
from biosignal.public_dataset import fetch_biosample

@pytest.mark.integration
def test_live_ncbi_biosample_record():
    if os.getenv("BIOSIGNAL_LIVE_NCBI") != "1":
        pytest.skip("set BIOSIGNAL_LIVE_NCBI=1 to run the live public-data test")
    record = fetch_biosample("SAMN05170351")
    assert record.biosample_accession == "SAMN05170351"
    assert record.organism == "Escherichia coli"
    assert record.collection_date == "2014-11-03"
    assert record.geo_loc_name == "USA"
    assert record.isolation_source == "urine"
