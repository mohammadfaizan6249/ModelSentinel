from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class FeatureSpec:
    name: str
    minimum: float
    maximum: float
    bins: int = 10


FEATURE_SPECS: List[FeatureSpec] = [
    FeatureSpec("credit_score", 300.0, 850.0),
    FeatureSpec("income", 20_000.0, 200_000.0),
    FeatureSpec("debt_ratio", 0.0, 1.0),
    FeatureSpec("loan_amount", 1_000.0, 50_000.0),
    FeatureSpec("employment_yrs", 0.0, 40.0),
    FeatureSpec("age", 18.0, 75.0),
]

FEATURE_NAMES = [feature.name for feature in FEATURE_SPECS]
FEATURE_INDEX: Dict[str, FeatureSpec] = {feature.name: feature for feature in FEATURE_SPECS}


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def sigmoid(value: float) -> float:
    clipped = clamp(value, -40.0, 40.0)
    return 1.0 / (1.0 + math.exp(-clipped))


def feature_vector(row: dict) -> List[float]:
    return [float(row[name]) for name in FEATURE_NAMES]


def default_probability(row: dict, environment_offset: float = 0.0) -> float:
    credit_component = (650.0 - float(row["credit_score"])) / 115.0
    income_component = (80_000.0 - float(row["income"])) / 55_000.0
    debt_component = (float(row["debt_ratio"]) - 0.33) / 0.18
    loan_component = (float(row["loan_amount"]) - 18_000.0) / 14_000.0
    employment_component = (6.0 - float(row["employment_yrs"])) / 8.0
    age_component = (34.0 - float(row["age"])) / 18.0

    logit = (
        -0.55
        + 1.75 * credit_component
        + 1.05 * income_component
        + 1.55 * debt_component
        + 0.72 * loan_component
        + 0.28 * employment_component
        + 0.18 * age_component
        + environment_offset
    )
    return sigmoid(logit)
