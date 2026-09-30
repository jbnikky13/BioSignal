"""Data-quality heuristics for AMR observations."""
from dataclasses import dataclass
from .models import AMRObservation
@dataclass(frozen=True)
class QualityAssessment:
    sample_score: float
    completeness_score: float
    temporal_score: float
    confidence_score: float
    label: str
    reasons: tuple[str, ...]
def assess_quality(observation: AMRObservation, *, target_samples: int = 100) -> QualityAssessment:
    reasons=[]
    sample_score=min(observation.tested_count/target_samples,1.0)
    if observation.tested_count<10: reasons.append("very small sample")
    elif observation.tested_count<target_samples: reasons.append("sample below configured target")
    completeness=1.0
    if not observation.region: completeness-=0.2; reasons.append("region unavailable")
    if not observation.source: completeness-=0.2; reasons.append("source metadata unavailable")
    days=(observation.period_end-observation.period_start).days+1
    temporal=min(days/90,1.0)
    if days<30: reasons.append("short observation window")
    confidence=round(max(0.0,min(1.0,0.5*sample_score+0.25*completeness+0.25*temporal)),3)
    label="higher_data_confidence" if confidence>=0.8 else "moderate_data_confidence" if confidence>=0.5 else "limited_data_confidence"
    return QualityAssessment(round(sample_score,3),round(completeness,3),round(temporal,3),confidence,label,tuple(reasons))
