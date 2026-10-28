"""Transparent, uncalibrated data-quality heuristics for AMR observations."""

from dataclasses import dataclass
import warnings

from .models import AMRObservation


@dataclass(frozen=True)
class QualityAssessment:
    """Heuristic data-quality scores; none are statistical confidence estimates.

    `data_quality_score` is a weighted engineering score in [0, 1], not a
    probability, calibrated confidence value, or measure of clinical validity.
    """

    sample_score: float
    completeness_score: float
    temporal_score: float
    data_quality_score: float
    data_quality_label: str
    reasons: tuple[str, ...]
    calibration_status: str = "uncalibrated_heuristic"

    @property
    def confidence_score(self) -> float:
        """Deprecated compatibility alias; use data_quality_score instead."""
        warnings.warn(
            "confidence_score is deprecated because this value is not statistical "
            "confidence; use data_quality_score instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.data_quality_score

    @property
    def label(self) -> str:
        """Deprecated compatibility alias; use data_quality_label instead."""
        warnings.warn(
            "label is deprecated; use data_quality_label instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.data_quality_label


def assess_quality(
    observation: AMRObservation,
    *,
    target_samples: int = 100,
) -> QualityAssessment:
    """Return a transparent engineering score, not calibrated statistical confidence.

    The weighted score is a configurable heuristic. It has not been calibrated
    against surveillance outcomes and must not be interpreted as a probability
    that an observation or signal is correct, or as clinical/epidemiological
    validation.
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
        "higher_data_quality_score"
        if score >= 0.8
        else "moderate_data_quality_score"
        if score >= 0.5
        else "limited_data_quality_score"
    )
    return QualityAssessment(
        sample_score=round(sample_score, 3),
        completeness_score=round(completeness, 3),
        temporal_score=round(temporal, 3),
        data_quality_score=score,
        data_quality_label=label,
        reasons=tuple(reasons),
    )
