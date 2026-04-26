from __future__ import annotations

import json
import os
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from ml.evaluation.metrics import evaluate_classifier
from ml.models.logistic_regression import CreditRiskModel, train_logistic_regression

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_model_dir() -> Path:
    override = os.environ.get("MODELSENTINEL_MODEL_DIR")
    if override:
        return Path(override)
    return Path(__file__).resolve().parents[1] / "models"


def get_registry_path() -> Path:
    return get_model_dir() / "model_registry.json"


def split_rows(rows: List[dict], holdout_ratio: float = 0.2, seed: int = 7) -> tuple[List[dict], List[dict]]:
    shuffled = list(rows)
    random.Random(seed).shuffle(shuffled)
    split_index = max(1, int(len(shuffled) * (1.0 - holdout_ratio)))
    return shuffled[:split_index], shuffled[split_index:]


def cross_validate(rows: List[dict], folds: int = 3) -> Dict[str, float]:
    shuffled = list(rows)
    random.Random(17).shuffle(shuffled)
    fold_size = max(1, len(shuffled) // folds)
    scores: List[float] = []

    for fold_index in range(folds):
        start = fold_index * fold_size
        end = len(shuffled) if fold_index == folds - 1 else start + fold_size
        validation_rows = shuffled[start:end]
        training_rows = shuffled[:start] + shuffled[end:]
        if not validation_rows or not training_rows:
            continue
        model = train_logistic_regression(training_rows)
        scores.append(evaluate_classifier(model, validation_rows)["accuracy"])

    mean_accuracy = sum(scores) / len(scores) if scores else 0.0
    return {"folds": folds, "accuracy": round(mean_accuracy, 4)}


@dataclass
class PipelineResult:
    version: str
    trained_at: str
    train_size: int
    validation_size: int
    cv_accuracy: float
    validation_accuracy: float
    validation_log_loss: float
    model: CreditRiskModel
    registry_path: str


def _serialize_model(model: CreditRiskModel) -> Dict:
    return {
        "feature_names": model.feature_names,
        "means": model.means,
        "stds": model.stds,
        "weights": model.weights,
        "bias": model.bias,
    }


def _load_registry() -> List[Dict]:
    registry_path = get_registry_path()
    if not registry_path.exists():
        return []
    entries = json.loads(registry_path.read_text())
    deduped: Dict[str, Dict] = {}
    for entry in entries:
        deduped[entry["version"]] = entry
    return list(deduped.values())


def _write_registry(entries: List[Dict]) -> None:
    model_dir = get_model_dir()
    registry_path = get_registry_path()
    model_dir.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(json.dumps(entries, indent=2))


def run_retraining_pipeline(training_rows: List[dict], version: str) -> PipelineResult:
    model_dir = get_model_dir()
    registry_path = get_registry_path()
    train_rows, validation_rows = split_rows(training_rows, holdout_ratio=0.2, seed=13)
    model = train_logistic_regression(train_rows)
    cv_metrics = cross_validate(train_rows, folds=3)
    validation_metrics = evaluate_classifier(model, validation_rows)

    artifact = {
        "version": version,
        "trained_at": utc_now_iso(),
        "train_size": len(train_rows),
        "validation_size": len(validation_rows),
        "cv_accuracy": cv_metrics["accuracy"],
        "validation_accuracy": validation_metrics["accuracy"],
        "validation_log_loss": validation_metrics["log_loss"],
        "model": _serialize_model(model),
    }

    model_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = model_dir / f"{version}.json"
    artifact_path.write_text(json.dumps(artifact, indent=2))

    registry = _load_registry()
    registry = [entry for entry in registry if entry["version"] != version]
    registry.append(
        {
            "version": version,
            "trained_at": artifact["trained_at"],
            "train_size": artifact["train_size"],
            "validation_size": artifact["validation_size"],
            "cv_accuracy": artifact["cv_accuracy"],
            "validation_accuracy": artifact["validation_accuracy"],
            "validation_log_loss": artifact["validation_log_loss"],
            "artifact_path": str(artifact_path),
        }
    )
    _write_registry(registry)

    return PipelineResult(
        version=version,
        trained_at=artifact["trained_at"],
        train_size=len(train_rows),
        validation_size=len(validation_rows),
        cv_accuracy=cv_metrics["accuracy"],
        validation_accuracy=validation_metrics["accuracy"],
        validation_log_loss=validation_metrics["log_loss"],
        model=model,
        registry_path=str(registry_path),
    )
