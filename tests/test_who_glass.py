import json
import subprocess
import sys
from pathlib import Path

import pytest

from biosignal.who_glass import parse_who_glass_export, summarize_country_years


HEADER = (
    '"Iso3","CountryTerritoryArea","WHORegionName","Year","Specimen",'
    '"PathogenName","AbTargets","TotalSpecimenIsolates","InterpretableAST",'
    '"Resistant","PercentResistant"'
)


def export(rows, *, pathogen="Escherichia coli", antibiotic="Ceftriaxone"):
    return "\n".join([
        "Filters",
        '"Region filter: All"',
        '"Infection type filter: Bloodstream"',
        f'"Bacterial pathogen filter: {pathogen}"',
        f'"Antibiotic filter: {antibiotic}"',
        "",
        "Data for time series",
        '"Year","Specimen","PathogenName","AbTargets","Min","Q1","Median","Q3","Max"',
        f'2018,"BLOOD","{pathogen}","{antibiotic}",1,2,3,4,5',
        "",
        "Data for line plots for individual CTAs",
        HEADER,
        *rows,
        "",
    ])


def record(country, year, total=100, tested=80, resistant=20, pathogen="Escherichia coli", antibiotic="Ceftriaxone"):
    pct = (100 * resistant / tested) if tested else 0
    return (
        f'"{country}","{country}","European Region",{year},"BLOOD",'
        f'"{pathogen}","{antibiotic}",{total},{tested},{resistant},{pct:.6f}'
    )


def test_importer_reads_country_rows_not_chart_quantiles():
    text = export([record("AAA", 2018), record("AAA", 2019, resistant=24)])
    metadata, rows = parse_who_glass_export(text)
    assert metadata["Bacterial pathogen filter"] == "Escherichia coli"
    assert len(rows) == 2
    assert rows[0]["Iso3"] == "AAA"
    assert rows[0]["Resistant"] == 20
    assert rows[0]["PercentResistant"] == 25.0


def test_importer_rejects_summary_only_or_wrong_export():
    with pytest.raises(ValueError, match="missing"):
        parse_who_glass_export('"Year","Min","Q1"\n2018,1,2')


@pytest.mark.parametrize(
    "bad_record, message",
    [
        (record("AAA", 2018, tested=0, resistant=0), "InterpretableAST must be positive"),
        (record("AAA", 2018, tested=80, resistant=81), "Resistant exceeds InterpretableAST"),
        (record("AAA", 2018, total=50, tested=80), "InterpretableAST exceeds TotalSpecimenIsolates"),
        (record("AAA", 2018).replace("25.000000", "90.000000"), "does not match"),
    ],
)
def test_importer_rejects_invalid_denominators_and_percentages(bad_record, message):
    with pytest.raises(ValueError, match=message):
        parse_who_glass_export(export([bad_record]))


def test_importer_rejects_duplicate_country_year():
    with pytest.raises(ValueError, match="duplicate country-year"):
        parse_who_glass_export(export([record("AAA", 2018), record("AAA", 2018, resistant=24)]))


def test_importer_rejects_filter_data_mismatch():
    wrong = record("AAA", 2018, pathogen="Klebsiella pneumoniae")
    with pytest.raises(ValueError, match="Bacterial pathogen filter"):
        parse_who_glass_export(export([wrong]))


def test_summary_labels_pooled_rates_as_descriptive_not_global():
    _, rows = parse_who_glass_export(export([
        record("AAA", 2018, tested=80, resistant=20),
        record("BBB", 2018, tested=20, resistant=10),
        record("AAA", 2019, tested=80, resistant=24),
        record("BBB", 2019, tested=20, resistant=5),
    ]))
    summary = summarize_country_years(rows)
    assert summary["country_year_rows"] == 4
    assert summary["countries"] == 2
    assert summary["balanced_country_panel"] is True
    assert summary["yearly_pooled_descriptive_rates"][0]["pooled_resistance_percent"] == 30.0
    assert "not global population estimates" in summary["interpretation"]
