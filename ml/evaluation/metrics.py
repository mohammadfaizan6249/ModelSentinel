from __future__ import annotations

import math
from typing import Dict, List

from ml.models.logistic_regression import CreditRiskModel


def evaluate_classifier(model: CreditRiskModel, rows: List[dict]) -> Dict[str, float]:
    probabilities = [model.predict_proba(row) for row in rows]
    labels = [int(row["defaulted"]) for row in rows]
    predictions = [1 if probability >= 0.5 else 0 for probability in probabilities]

    accuracy = sum(int(prediction == label) for prediction, label in zip(predictions, labels)) / len(rows)
    positive_rate = sum(predictions) / len(rows)
    default_rate = sum(labels) / len(rows)
    log_loss = -sum(
        label * math.log(max(probability, 1e-6))
        + (1 - label) * math.log(max(1.0 - probability, 1e-6))
        for label, probability in zip(labels, probabilities)
    ) / len(rows)

    return {
        "accuracy": round(accuracy, 4),
        "positive_rate": round(positive_rate, 4),
        "default_rate": round(default_rate, 4),
        "log_loss": round(log_loss, 4),
    }
