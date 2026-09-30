# Public integration fixtures

BioSignal uses public NCBI BioSample SAMN05170351 as its first metadata integration fixture. NCBI documents this record as an Escherichia coli isolate with an antibiogram and sequencing data.

The fixture is metadata-only. No patient-identifying information or private medical records are included.

Source:
https://www.ncbi.nlm.nih.gov/biosample/SAMN05170351

The live integration test is opt-in:
BIOSIGNAL_LIVE_NCBI=1 pytest -m integration

Expected values are based on the public NCBI record and should be refreshed if NCBI changes the record.
