"""
risk_classifier.py
-------------------
Demo risk classification based on the *rate/percentage* of detected
coastal change. This is NOT a scientifically validated coastal-risk
model — it is a simple, documented, easily-tunable rule used to make
the MVP demo-able. All thresholds live in utils.PipelineConfig so they
are easy to find and change (see SCHEMA.md).

Future extension: replace this function's body with a model trained on
real historical erosion-rate / risk-outcome data, without changing its
signature.
"""

from __future__ import annotations

LOW = "Low"
MEDIUM = "Medium"
HIGH = "High"


def classify_risk(
    percent_change: float,
    low_max_pct: float = 2.0,
    medium_max_pct: float = 5.0,
) -> str:
    """
    Classify coastal-change risk from absolute percentage change.

    MVP thresholds:
        abs(change) < 2%       -> Low
        2% <= abs(change) <= 5% -> Medium
        abs(change) > 5%       -> High

    These are hackathon MVP thresholds and are not
    scientifically validated coastal-risk thresholds.
    """

    if low_max_pct < 0 or medium_max_pct <= low_max_pct:
        raise ValueError("Require 0 <= low_max_pct < medium_max_pct")

    magnitude = abs(percent_change)

    if magnitude < low_max_pct:
        return LOW
    elif magnitude <= medium_max_pct:
        return MEDIUM
    else:
        return HIGH