from unittest.mock import patch
import json
import pytest

from biosignal.ncbi_genome import find_assemblies_by_biosample


class Response:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def read(self):
        return json.dumps(self.payload).encode()


def test_resolves_public_assembly_from_legacy_shape():
    payload = {
        "reports": [{
            "assembly_info": {
                "assembly_accession": "GCA_123456.1",
                "assembly_name": "ASM123",
                "assembly_level": "Complete Genome",
                "biosample": {"accession": "SAMN05170351"},
                "bioproject_lineage": [{"accession": "PRJNA288601"}],
            },
            "organism": {"organism_name": "Escherichia coli"},
        }]
    }
    with patch("biosignal.ncbi_genome.urlopen", return_value=Response(payload)):
        result = find_assemblies_by_biosample("SAMN05170351")

    assert result[0].assembly_accession == "GCA_123456.1"
    assert result[0].biosample_accession == "SAMN05170351"


def test_resolves_public_assembly_from_current_ncbi_shape():
    payload = {
        "reports": [{
            "accession": "GCA_012849755.1",
            "assemblyInfo": {
                "assemblyName": "Complete genome 2",
                "assemblyLevel": "complete",
                "biosample": {"accession": "SAMN05215988"},
                "bioprojectAccession": "PRJNA230969",
            },
            "organism": {"organismName": "Escherichia coli O121"},
        }]
    }
    with patch("biosignal.ncbi_genome.urlopen", return_value=Response(payload)):
        result = find_assemblies_by_biosample("SAMN05215988")

    assert result[0].assembly_accession == "GCA_012849755.1"
    assert result[0].biosample_accession == "SAMN05215988"
    assert result[0].organism == "Escherichia coli O121"
    assert result[0].bioproject_accession == "PRJNA230969"


def test_rejects_invalid_biosample_accession():
    with pytest.raises(ValueError, match="invalid BioSample"):
        find_assemblies_by_biosample("not-a-biosample")


def test_filters_mismatched_biosample_and_prefers_complete_refseq():
    payload = {
        "reports": [
            {
                "accession": "GCA_999999.1",
                "assemblyInfo": {
                    "assemblyLevel": "contig",
                    "biosample": {"accession": "SAMN99999999"},
                },
            },
            {
                "accession": "GCA_100000.1",
                "assemblyInfo": {
                    "assemblyLevel": "complete",
                    "biosample": {"accession": "SAMN05215988"},
                },
            },
            {
                "accession": "GCF_100000.1",
                "assemblyInfo": {
                    "assemblyLevel": "complete",
                    "biosample": {"accession": "SAMN05215988"},
                },
            },
        ]
    }
    with patch("biosignal.ncbi_genome.urlopen", return_value=Response(payload)):
        result = find_assemblies_by_biosample("SAMN05215988")

    assert [r.assembly_accession for r in result] == [
        "GCF_100000.1",
        "GCA_100000.1",
    ]
