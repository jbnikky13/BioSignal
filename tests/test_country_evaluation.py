import pytest
from biosignal.country_evaluation import evaluate_country_holdout, validate_protocol

def record(country, outcome, current, previous, protocol_id="AMR-EXPERT-v1"):
    return {"period_end":"2025-01-01","organism":"E. coli","antimicrobial":"ceftriaxone","region":"region",
      "source":"test surveillance source","dataset_release":"test release","coverage_notes":"synthetic unit-test record only",
      "current_rate":current,"previous_rate":previous,"sample_count":100,"previous_sample_count":100,
      "reference_outcome":outcome,"reference_source":"independent expert protocol","protocol_id":protocol_id,
      "surveillance_unit":country}

def protocol():
    return {"protocol_id":"AMR-EXPERT-v1","outcome_definition":"Expert-adjudicated, pre-specified AMR event",
      "expert_approval":{"status":"approved","expert_role":"AMR epidemiologist","approval_date":"2026-10-28","approval_reference":"synthetic test fixture"},
      "protocol_frozen_before_holdout_review":True,"holdout_countries":["HOLDOUT-A"],
      "thresholds":{"alert_rate":0.2,"alert_change_percentage_points":10,"minimum_samples":20},
      "baseline_thresholds":{"current_rate":0.2,"change_percentage_points":10}}

def test_requires_expert_approval():
    p=protocol(); p["expert_approval"]["status"]="pending"
    with pytest.raises(ValueError, match="must be 'approved'"): validate_protocol(p)

def test_country_holdout_compares_frozen_rules_and_baselines():
    rows=[record("DEV-A",0,.05,.04),record("DEV-B",1,.50,.10),record("HOLDOUT-A",1,.40,.10),record("HOLDOUT-A",0,.05,.04)]
    result=evaluate_country_holdout(rows,protocol())
    assert result["development_countries"] == ["DEV-A","DEV-B"]
    assert result["holdout_countries"] == ["HOLDOUT-A"] and result["holdout_records"] == 2
    assert set(result["metrics_by_rule"]) == {"always_negative","current_rate_baseline","change_only_baseline","biosignal_combined_rule"}
    assert result["metrics_by_rule"]["always_negative"]["false_negative"] == 1
    assert result["holdout_country_breakdown"]["HOLDOUT-A"]["records"] == 2

def test_protocol_id_must_match_labelled_rows():
    with pytest.raises(ValueError, match="protocol_id"):
        evaluate_country_holdout([record("HOLDOUT-A",1,.4,.1,"OTHER")],protocol())

def test_holdout_country_must_exist():
    with pytest.raises(ValueError, match="absent from dataset"):
        evaluate_country_holdout([record("DEV-A",0,.05,.04)],protocol())
