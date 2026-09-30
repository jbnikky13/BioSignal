from biosignal.genomics import genome_query, genome_download_command


def test_genome_query_is_bounded():
    command = genome_query(562, limit=5)
    assert command[:4] == ["datasets", "summary", "genome", "taxon"]
    assert "--limit" in command
    assert "5" in command


def test_download_requests_sequence_and_annotation():
    command = genome_download_command(562)
    assert "--include" in command
    assert "genome,gff3,seq-report" in command
