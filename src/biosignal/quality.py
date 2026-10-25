"""Transparent, uncalibrated data-quality heuristics for AMR observations."""

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
    calibration_status: str = "uncalibrated_heuristic"


def assess_quality(
    observation: AMRObservation,
    *,
    target_samples: int = 100,
) -> QualityAssessment:
    """Return transparent quality heuristics, not calibrated statistical confidence.

    The weighted score is a configurable engineering heuristic. It has not
    been calibrated against surveillance outcomes and must not be interpreted
    as a probability that an observation or signal is correct.
    """
    if target_samples <= 0:
        raise ValueError("target_samples must be greater than zero")

    reasons: list[str] = []
    sample_score = min(observation.tested_count / target_samples, 1.0)
    if observation.tested_count < 10:
        reasons.append("very small sample")
    elif observation.tested_count < target_samples:
        reasons.append("sample below configured target")

    completeness = 1.0
    if not observation.region:
        completeness -= 0.2
        reasons.append("region unavailable")
    if not observation.source:
        completeness -= 0.2
        reasons.append("source metadata unavailable")

    days = (observation.period_end - observation.period_start).days + 1
    temporal = min(days / 90, 1.0)
    if days < 30:
        reasons.append("short observation window")

    score = round(
        max(0.0, min(1.0, 0.5 * sample_score + 0.25 * completeness + 0.25 * temporal)),
        3,
    )
    label = (
        "higher_data_confidence"
        if score >= 0.8
        else "moderate_data_confidence"
        if score >= 0.5
        else "limited_data_confidence"
    )
    return QualityAssessment(
        sample_score=round(sample_score, 3),
        completeness_score=round(completeness, 3),
        temporal_score=round(temporal, 3),
        confidence_score=score,
        label=label,
        reasons=tuple(reasons),
    )
