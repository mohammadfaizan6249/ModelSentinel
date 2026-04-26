from __future__ import annotations

from collections import deque
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Deque, Dict, List

from ml.evaluation.metrics import evaluate_classifier
from ml.features.credit_risk import FEATURE_NAMES, FEATURE_SPECS
from ml.pipelines.retrain import PipelineResult, run_retraining_pipeline
from services.monitoring.drift.metrics import compare_feature
from services.monitoring.simulator.synthetic_data import generate_credit_risk_population


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class FeatureObservation:
    name: str
    psi: float
    ks: float
    baseline_distribution: List[float]
    current_distribution: List[float]
    trend_series: List[float]
    drift_delta: float


class MonitoringEngine:
    def __init__(self) -> None:
        self._baseline_seed = 31
        self._current_seed = 97
        self._history_seed = 131
        self._live_tick = 0
        self._severity = 0.62
        self._environment_offset = 0.15
        self._version_minor = 1
        self._batch_history: Deque[List[dict]] = deque(maxlen=18)
        self._reference_rows = generate_credit_risk_population(
            size=2400,
            severity=0.0,
            seed=self._baseline_seed,
            environment_offset=0.0,
        )
        self._current_rows = generate_credit_risk_population(
            size=900,
            severity=self._severity,
            seed=self._current_seed,
            environment_offset=self._environment_offset,
        )
        self._history_batches = self._build_history_batches()
        self._batch_history.extend(deepcopy(batch) for batch in self._history_batches[-8:])
        self._batch_history.append(deepcopy(self._current_rows))
        self._trend_history: Dict[str, List[float]] = {name: [] for name in FEATURE_NAMES}
        self._pipeline_result = self._bootstrap_model("CreditRisk_v2.1")
        self._snapshot = self._compute_snapshot()

    @property
    def snapshot(self) -> dict:
        return deepcopy(self._snapshot)

    def refresh(self) -> dict:
        self._current_seed += 1
        self._current_rows = generate_credit_risk_population(
            size=900,
            severity=self._severity,
            seed=self._current_seed,
            environment_offset=self._environment_offset,
        )
        self._batch_history.append(deepcopy(self._current_rows))
        self._snapshot = self._compute_snapshot()
        return deepcopy(self._snapshot)

    def live_tick(self) -> dict:
        self._live_tick += 1
        self._severity = max(0.08, min(0.82, self._severity + 0.015 - ((self._live_tick % 4) * 0.004)))
        self._environment_offset = max(0.04, min(0.24, self._environment_offset + 0.01 - ((self._live_tick % 3) * 0.006)))
        return self.refresh()

    def run_retraining(self) -> dict:
        recent_rows = self._recent_training_window()
        next_version = f"CreditRisk_v2.{self._version_minor + 1}"
        self._pipeline_result = run_retraining_pipeline(recent_rows, version=next_version)
        self._reference_rows = recent_rows
        self._version_minor += 1
        self._severity = max(0.12, self._severity - 0.06)
        self._environment_offset = max(0.03, self._environment_offset - 0.04)
        self._current_seed += 11
        self._current_rows = generate_credit_risk_population(
            size=900,
            severity=self._severity,
            seed=self._current_seed,
            environment_offset=self._environment_offset,
        )
        history_tail = self._build_history_batches()[8:]
        self._history_batches = [deepcopy(self._reference_rows) for _ in range(8)] + history_tail
        self._batch_history.clear()
        self._batch_history.extend(deepcopy(batch) for batch in self._history_batches[-8:])
        self._batch_history.append(deepcopy(self._current_rows))
        self._trend_history = {name: [] for name in FEATURE_NAMES}
        self._snapshot = self._compute_snapshot()
        return deepcopy(self._snapshot)

    def create_analysis(self) -> dict:
        features = sorted(self._snapshot["features"], key=lambda feature: feature["psi"], reverse=True)
        top_feature = features[0]
        second_feature = features[1]
        drifted = [feature for feature in features if feature["status"] != "stable"]
        return {
            "generated_at": utc_now(),
            "note": (
                "Phases 3 and 4 now use real synthetic production batches, computed PSI/KS drift, "
                "and a trained logistic model with versioned retraining artifacts."
            ),
            "sections": [
                {
                    "title": "Root Cause Analysis",
                    "body": (
                        f"{top_feature['name']} now leads drift based on computed PSI {top_feature['psi']:.2f} and KS {top_feature['ks']:.2f}. "
                        f"The secondary movement in {second_feature['name']} points to a real shift in the simulated applicant mix rather than seeded UI values."
                    ),
                },
                {
                    "title": "Business Impact",
                    "body": (
                        f"{len(drifted)} features are outside the stable range and the current model accuracy is {self._snapshot['current_accuracy']:.3f} "
                        f"versus {self._snapshot['baseline_accuracy']:.3f} on the reference population. That gap indicates the deployed scorer is degrading on the live segment mix."
                    ),
                },
                {
                    "title": "Immediate Actions",
                    "body": (
                        "Inspect the freshest production batch, compare the current applicant cohort with the historical reference window, "
                        "and validate whether feature transformations or business conditions are driving the distribution changes."
                    ),
                },
                {
                    "title": "Long-Term Fixes",
                    "body": (
                        f"Keep daily drift snapshots, persist model versions in {self._pipeline_result.registry_path}, and retrain on rolling recent windows when drift and performance degradation move together."
                    ),
                },
            ],
        }

    def _bootstrap_model(self, version: str) -> PipelineResult:
        return run_retraining_pipeline(self._reference_rows, version=version)

    def _recent_training_window(self) -> List[dict]:
        history = list(self._batch_history) if self._batch_history else [self._current_rows]
        merged: List[dict] = []
        for batch in history[-12:]:
            merged.extend(deepcopy(batch))
        if not merged:
            merged = deepcopy(self._current_rows)
        return merged

    def _build_history_batches(self) -> List[List[dict]]:
        batches: List[List[dict]] = []
        for index in range(24):
            severity = max(0.05, min(self._severity, self._severity * (0.30 + (0.70 * index / 23.0))))
            seed = self._history_seed + index
            batches.append(
                generate_credit_risk_population(
                    size=700,
                    severity=severity,
                    seed=seed,
                    environment_offset=max(0.0, self._environment_offset * (0.4 + 0.6 * index / 23.0)),
                )
            )
        return batches

    def _feature_observations(self) -> List[FeatureObservation]:
        observations: List[FeatureObservation] = []
        for spec in FEATURE_SPECS:
            reference_values = [float(row[spec.name]) for row in self._reference_rows]
            current_values = [float(row[spec.name]) for row in self._current_rows]
            baseline_distribution, current_distribution, feature_psi, feature_ks = compare_feature(
                reference_values,
                current_values,
                lower=spec.minimum,
                upper=spec.maximum,
                bins=spec.bins,
            )

            history_series = []
            for batch in self._history_batches:
                batch_values = [float(row[spec.name]) for row in batch]
                _, _, history_psi, _ = compare_feature(
                    reference_values,
                    batch_values,
                    lower=spec.minimum,
                    upper=spec.maximum,
                    bins=spec.bins,
                )
                history_series.append(history_psi)
            history_series[-1] = feature_psi

            previous_psi = self._trend_history[spec.name][-1] if self._trend_history[spec.name] else history_series[-2]
            observations.append(
                FeatureObservation(
                    name=spec.name,
                    psi=feature_psi,
                    ks=feature_ks,
                    baseline_distribution=baseline_distribution,
                    current_distribution=current_distribution,
                    trend_series=history_series,
                    drift_delta=feature_psi - previous_psi,
                )
            )
        return observations

    def _compute_snapshot(self) -> dict:
        observations = self._feature_observations()
        features = []
        for observation in observations:
            status = self._status(observation.psi)
            features.append(
                {
                    "name": observation.name,
                    "psi": observation.psi,
                    "ks": observation.ks,
                    "status": status,
                    "trend": self._trend(observation.drift_delta),
                    "baseline_distribution": observation.baseline_distribution,
                    "current_distribution": observation.current_distribution,
                    "trend_series": observation.trend_series,
                    "last_updated_at": utc_now(),
                }
            )
            self._trend_history[observation.name] = observation.trend_series

        baseline_metrics = evaluate_classifier(self._pipeline_result.model, self._reference_rows[:600])
        current_metrics = evaluate_classifier(self._pipeline_result.model, self._current_rows)
        health_percent = round((current_metrics["accuracy"] / max(baseline_metrics["accuracy"], 1e-6)) * 100)
        health_delta = (current_metrics["accuracy"] - baseline_metrics["accuracy"]) * 100.0
        health_label = (
            f"accuracy gain: {health_delta:+.1f}%"
            if health_delta > 0
            else f"accuracy drop: {health_delta:+.1f}%"
        )

        return {
            "model_name": self._pipeline_result.version,
            "environment": "prod-us-east",
            "features": features,
            "alerts": self._create_alerts(features),
            "monitored_features_delta": "+2 this week",
            "last_updated_at": utc_now(),
            "baseline_accuracy": baseline_metrics["accuracy"],
            "current_accuracy": current_metrics["accuracy"],
            "validation_accuracy": self._pipeline_result.validation_accuracy,
            "health_percent": max(18, min(100, health_percent)),
            "health_delta_text": health_label,
        }

    def _create_alerts(self, features: List[dict]) -> List[dict]:
        alerts = []
        ordered = sorted(features, key=lambda feature: feature["psi"], reverse=True)
        for index, feature in enumerate(item for item in ordered if item["status"] != "stable"):
            level = "critical" if feature["status"] == "critical" else "warning"
            message = (
                f"Computed PSI {feature['psi']:.2f} exceeded threshold and KS reached {feature['ks']:.2f}. "
                if level == "critical"
                else f"Computed PSI {feature['psi']:.2f} indicates moderate drift and KS is {feature['ks']:.2f}. "
            )
            detail = (
                "Credit score distribution has shifted toward weaker applicants."
                if feature["name"] == "credit_score"
                else "Income mix has moved downward compared with the training reference."
                if feature["name"] == "income"
                else "Debt burden is trending upward across the live population."
                if feature["name"] == "debt_ratio"
                else "The feature distribution is materially different from the reference cohort."
            )
            alerts.append(
                {
                    "id": f"{feature['name']}-{index}",
                    "level": level,
                    "feature": feature["name"],
                    "message": message + detail,
                    "time_ago": f"{14 + index * 21} mins ago",
                }
            )
        return alerts

    def _status(self, psi: float) -> str:
        if psi > 0.25:
            return "critical"
        if psi > 0.10:
            return "warning"
        return "stable"

    def _trend(self, delta: float) -> str:
        if delta > 0.004:
            return "up"
        if delta < -0.004:
            return "down"
        return "flat"
