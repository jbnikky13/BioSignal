"""Data-quality and confidence metrics for AMR observations.

These metrics are intentionally transparent heuristics. They do not estimate
clinical risk or replace WHO/epidemiological methodology.
"""

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


def assess_quality(
    observation: AMRObservation,
    *,
    target_samples: int = 100,
) -> QualityAssessment:
    reasons: list[str] = []

    sample_score = min(observation.tested_count / target_samples, 1.0)
    if observation.tested_count < 10:
        reasons.append("very small sample")
    elif observation.tested_count < target_samples:
        reasons.append("sample below configured target")

    completeness_score = 1.0
    if not observation.region:
        completeness_score -= 0.20
        reasons.append("region unavailable")
    if not observation.source:
        completeness_score -= 0.20
        reasons.append("source metadata unavailable")

    days = (observation.period_end - observation.period_start).days + 1
    temporal_score = min(days / 90, 1.0)
    if days < 30:
        reasons.append("short observation window")

    confidence = round(
        max(0.0, min(1.0, 0.50 * sample_score
        + 0.25 * completeness_score
        + 0.25 * temporal_score)),
        3,
    )

    if confidence >= 0.80:
        label = "higher_data_confidence"
    elif confidence >= 0.50:
        label = "moderate_data_confidence"
    else:
        label = "limited_data_confidence"

    return QualityAssessment(
        sample_score=round(sample_score, 3),
        completeness_score=round(completeness_score, 3),
        temporal_score=round(temporal_score, 3),
        confidence_score=confidence,
        label=label,
        reasons=tuple(reasons),
    )
