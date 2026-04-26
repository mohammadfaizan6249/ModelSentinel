from __future__ import annotations

import random
from typing import Dict, List

from ml.features.credit_risk import FEATURE_INDEX, clamp, default_probability


def _sample_gaussian(rng: random.Random, mean: float, stddev: float, lower: float, upper: float) -> float:
    return round(clamp(rng.gauss(mean, stddev), lower, upper), 3)


def generate_credit_risk_population(
    size: int,
    severity: float,
    seed: int,
    environment_offset: float,
) -> List[dict]:
    rng = random.Random(seed)
    rows: List[dict] = []

    credit_shift = 52.0 * severity
    income_shift = 17_000.0 * severity
    debt_shift = 0.085 * severity
    loan_shift = 6_000.0 * severity
    employment_shift = 1.6 * severity
    age_shift = 2.1 * severity

    for _ in range(size):
        row = {
            "credit_score": _sample_gaussian(
                rng, 710.0 - credit_shift, 58.0 + 10.0 * severity, FEATURE_INDEX["credit_score"].minimum, FEATURE_INDEX["credit_score"].maximum
            ),
            "income": _sample_gaussian(
                rng, 92_000.0 - income_shift, 19_000.0 + 6_000.0 * severity, FEATURE_INDEX["income"].minimum, FEATURE_INDEX["income"].maximum
            ),
            "debt_ratio": _sample_gaussian(
                rng, 0.28 + debt_shift, 0.08 + 0.02 * severity, FEATURE_INDEX["debt_ratio"].minimum, FEATURE_INDEX["debt_ratio"].maximum
            ),
            "loan_amount": _sample_gaussian(
                rng, 18_000.0 + loan_shift, 6_200.0 + 1_800.0 * severity, FEATURE_INDEX["loan_amount"].minimum, FEATURE_INDEX["loan_amount"].maximum
            ),
            "employment_yrs": _sample_gaussian(
                rng, 8.5 - employment_shift, 4.6 + 0.9 * severity, FEATURE_INDEX["employment_yrs"].minimum, FEATURE_INDEX["employment_yrs"].maximum
            ),
            "age": _sample_gaussian(
                rng, 42.0 - age_shift, 10.0 + 1.2 * severity, FEATURE_INDEX["age"].minimum, FEATURE_INDEX["age"].maximum
            ),
        }
        probability = default_probability(row, environment_offset=environment_offset)
        row["defaulted"] = 1 if rng.random() < probability else 0
        rows.append(row)

    return rows
