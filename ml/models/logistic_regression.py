from __future__ import annotations

from dataclasses import dataclass
from typing import List

from ml.features.credit_risk import FEATURE_NAMES, feature_vector, sigmoid


@dataclass
class CreditRiskModel:
    feature_names: List[str]
    means: List[float]
    stds: List[float]
    weights: List[float]
    bias: float

    def predict_proba(self, row: dict) -> float:
        scaled = []
        for value, mean, stddev in zip(feature_vector(row), self.means, self.stds):
            scaled.append((value - mean) / stddev)
        score = self.bias + sum(weight * value for weight, value in zip(self.weights, scaled))
        return sigmoid(score)

    def predict(self, row: dict, threshold: float = 0.5) -> int:
        return 1 if self.predict_proba(row) >= threshold else 0


def _fit_scaler(rows: List[dict]) -> tuple[List[float], List[float]]:
    means: List[float] = []
    stds: List[float] = []
    for name in FEATURE_NAMES:
        values = [float(row[name]) for row in rows]
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        means.append(mean)
        stds.append(max(variance ** 0.5, 1e-6))
    return means, stds


def _scale_rows(rows: List[dict], means: List[float], stds: List[float]) -> List[List[float]]:
    matrix: List[List[float]] = []
    for row in rows:
        matrix.append(
            [(value - mean) / stddev for value, mean, stddev in zip(feature_vector(row), means, stds)]
        )
    return matrix


def train_logistic_regression(
    rows: List[dict],
    epochs: int = 260,
    learning_rate: float = 0.16,
    l2_penalty: float = 0.002,
) -> CreditRiskModel:
    means, stds = _fit_scaler(rows)
    matrix = _scale_rows(rows, means, stds)
    labels = [int(row["defaulted"]) for row in rows]
    weights = [0.0 for _ in FEATURE_NAMES]
    bias = 0.0
    size = float(len(rows))

    for _ in range(epochs):
        gradients = [0.0 for _ in FEATURE_NAMES]
        bias_gradient = 0.0

        for features, label in zip(matrix, labels):
            probability = sigmoid(sum(weight * value for weight, value in zip(weights, features)) + bias)
            error = probability - label
            bias_gradient += error
            for index, value in enumerate(features):
                gradients[index] += error * value

        for index in range(len(weights)):
            gradients[index] = (gradients[index] / size) + l2_penalty * weights[index]
            weights[index] -= learning_rate * gradients[index]

        bias -= learning_rate * (bias_gradient / size)

    return CreditRiskModel(
        feature_names=list(FEATURE_NAMES),
        means=means,
        stds=stds,
        weights=weights,
        bias=bias,
    )
