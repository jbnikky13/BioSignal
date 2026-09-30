from unittest.mock import patch
import json
from biosignal.ncbi_genome import find_assemblies_by_biosample

def test_resolves_public_assembly_from_biosample():
    payload={"reports":[{"assembly_info":{"assembly_accession":"GCA_123456.1","assembly_name":"ASM123","assembly_level":"Complete Genome","biosample":{"accession":"SAMN05170351"},"bioproject_lineage":[{"accession":"PRJNA288601"}]},"organism":{"organism_name":"Escherichia coli"}}]}
    class Response:
        def __enter__(self): return self
        def __exit__(self,*args): pass
        def read(self): return json.dumps(payload).encode()
    with patch("biosignal.ncbi_genome.urlopen", return_value=Response()):
        result=find_assemblies_by_biosample("SAMN05170351")
    assert result[0].assembly_accession=="GCA_123456.1"
    assert result[0].biosample_accession=="SAMN05170351"
