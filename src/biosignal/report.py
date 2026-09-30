"""Human-readable signal reporting."""

from .signals import AMRSignal


def to_dict(signal: AMRSignal) -> dict:
    return {
        "organism": signal.organism,
        "antimicrobial": signal.antimicrobial,
        "current_rate": signal.current_rate,
        "previous_rate": signal.previous_rate,
        "change": signal.change,
        "sample_count": signal.sample_count,
        "region": signal.region,
        "severity": signal.severity,
        "explanation": signal.explanation,
    }
