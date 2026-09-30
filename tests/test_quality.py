from datetime import date
from biosignal.models import AMRObservation
from biosignal.quality import assess_quality
def test_quality_penalizes_missing_metadata():
    obs=AMRObservation(organism="E. coli",antimicrobial="ciprofloxacin",period_start=date(2026,1,1),period_end=date(2026,3,31),tested_count=25,resistant_count=10)
    assessment=assess_quality(obs)
    assert assessment.confidence_score<0.8
    assert "region unavailable" in assessment.reasons
def test_complete_large_period_scores_higher():
    obs=AMRObservation(organism="E. coli",antimicrobial="ciprofloxacin",period_start=date(2026,1,1),period_end=date(2026,3,31),tested_count=100,resistant_count=20,region="Nigeria",source="WHO GLASS-AMR")
    assessment=assess_quality(obs)
    assert assessment.confidence_score==1.0
    assert assessment.label=="higher_data_confidence"
