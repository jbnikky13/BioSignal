from biosignal.surveillance import summarize_geography_time

def row(iso3, country, region, year, tested, resistant):
    return {
        "Iso3": iso3, "CountryTerritoryArea": country, "WHORegionName": region,
        "Year": year, "Specimen": "BLOOD", "PathogenName": "Escherichia coli",
        "AbTargets": "Ceftriaxone", "TotalSpecimenIsolates": tested + 5,
        "InterpretableAST": tested, "Resistant": resistant,
        "PercentResistant": 100 * resistant / tested,
    }

def test_region_year_summary_preserves_denominators_and_country_coverage():
    rows = [
        row("AAA", "Alpha", "Region One", 2020, 80, 20),
        row("BBB", "Beta", "Region One", 2020, 20, 10),
        row("AAA", "Alpha", "Region One", 2021, 80, 24),
        row("CCC", "Gamma", "Region Two", 2020, 50, 5),
    ]
    result = summarize_geography_time(rows)
    one = next(item for item in result["region_year"] if item["who_region"] == "Region One" and item["year"] == 2020)
    assert one["countries_reporting"] == 2
    assert one["resistant_count"] == 30
    assert one["interpretable_ast_count"] == 100
    assert one["pooled_resistance_percent"] == 30.0
    assert "not population-representative" in result["interpretation"]

def test_region_year_summary_does_not_fill_missing_country_years():
    rows = [
        row("AAA", "Alpha", "Region One", 2020, 80, 20),
        row("AAA", "Alpha", "Region One", 2022, 80, 30),
        row("BBB", "Beta", "Region One", 2020, 20, 10),
    ]
    result = summarize_geography_time(rows)
    assert [item["year"] for item in result["region_year"]] == [2020, 2022]
    assert result["country_coverage"][0]["years_reported"] == [2020, 2022]
    assert result["country_coverage"][1]["years_reported"] == [2020]
