from __future__ import annotations

import sys
import threading
import uuid
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import HTTPException

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from services.monitoring.simulator.engine import MonitoringEngine  # noqa: E402

from app.schemas.dashboard import (  # noqa: E402
    AiAnalysisResult,
    AlertItem,
    DashboardSnapshot,
    FeatureDistribution,
    FeatureMetric,
    FeatureTrend,
    RetrainingJob,
    RetrainingJobStatus,
    RetrainingProgress,
)

RETRAINING_STEPS: list[RetrainingProgress] = [
    RetrainingProgress(progress=10, label="Loading 90 days of production training data..."),
    RetrainingProgress(progress=24, label="Validating schema and preprocessing features..."),
    RetrainingProgress(progress=44, label="Training fold 1/3 on refreshed population..."),
    RetrainingProgress(progress=63, label="Training fold 2/3 on refreshed population..."),
    RetrainingProgress(progress=82, label="Training fold 3/3 and evaluating holdout..."),
    RetrainingProgress(progress=94, label="Registering CreditRisk_v2.2 candidate..."),
    RetrainingProgress(progress=100, label="Deploy complete. New reference window is active."),
]

STEP_DURATION_SECONDS = 0.75


@dataclass
class JobState:
    job_id: str
    started_at: datetime
    applied: bool = False
    completed_at: Optional[datetime] = None


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DashboardState:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._jobs: dict[str, JobState] = {}
        self._engine = MonitoringEngine()

    def get_snapshot(self) -> DashboardSnapshot:
        with self._lock:
            return DashboardSnapshot.model_validate(deepcopy(self._engine.snapshot))

    def get_features(self) -> list[FeatureMetric]:
        with self._lock:
            snapshot = self._engine.snapshot
            return [FeatureMetric.model_validate(feature) for feature in snapshot["features"]]

    def get_alerts(self) -> list[AlertItem]:
        with self._lock:
            snapshot = self._engine.snapshot
            return [AlertItem.model_validate(alert) for alert in snapshot["alerts"]]

    def get_distribution(self, feature_name: str) -> FeatureDistribution:
        with self._lock:
            snapshot = self._engine.snapshot
            for feature in snapshot["features"]:
                if feature["name"] == feature_name:
                    return FeatureDistribution.model_validate(
                        {
                            "feature_name": feature_name,
                            "baseline_distribution": feature["baseline_distribution"],
                            "current_distribution": feature["current_distribution"],
                            "last_updated_at": feature["last_updated_at"],
                        }
                    )
        raise HTTPException(status_code=404, detail=f"Feature '{feature_name}' not found.")

    def get_trend(self, feature_name: str) -> FeatureTrend:
        with self._lock:
            snapshot = self._engine.snapshot
            for feature in snapshot["features"]:
                if feature["name"] == feature_name:
                    return FeatureTrend.model_validate(
                        {
                            "feature_name": feature_name,
                            "psi_threshold_warning": 0.10,
                            "psi_threshold_critical": 0.25,
                            "series": feature["trend_series"],
                            "last_updated_at": feature["last_updated_at"],
                        }
                    )
        raise HTTPException(status_code=404, detail=f"Feature '{feature_name}' not found.")

    def refresh_snapshot(self) -> DashboardSnapshot:
        with self._lock:
            snapshot = self._engine.refresh()
            return DashboardSnapshot.model_validate(deepcopy(snapshot))

    def live_tick(self) -> DashboardSnapshot:
        with self._lock:
            snapshot = self._engine.live_tick()
            return DashboardSnapshot.model_validate(deepcopy(snapshot))

    def create_analysis(self) -> AiAnalysisResult:
        with self._lock:
            return AiAnalysisResult.model_validate(self._engine.create_analysis())

    def start_retraining(self) -> RetrainingJob:
        with self._lock:
            job_id = uuid.uuid4().hex
            started_at = utc_now()
            self._jobs[job_id] = JobState(job_id=job_id, started_at=started_at)
            return RetrainingJob(
                job_id=job_id,
                status=RetrainingJobStatus.queued,
                started_at=started_at,
                current_step=RETRAINING_STEPS[0],
            )

    def get_retraining_job(self, job_id: str) -> RetrainingJob:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                raise HTTPException(status_code=404, detail="Retraining job not found.")

            elapsed = max(0.0, (utc_now() - job.started_at).total_seconds())
            step_index = min(int(elapsed // STEP_DURATION_SECONDS), len(RETRAINING_STEPS) - 1)
            is_complete = elapsed >= STEP_DURATION_SECONDS * len(RETRAINING_STEPS)

            if is_complete and not job.applied:
                snapshot = self._engine.run_retraining()
                job.applied = True
                job.completed_at = utc_now()
                return RetrainingJob(
                    job_id=job.job_id,
                    status=RetrainingJobStatus.completed,
                    started_at=job.started_at,
                    completed_at=job.completed_at,
                    current_step=None,
                    snapshot=DashboardSnapshot.model_validate(snapshot),
                )

            status = (
                RetrainingJobStatus.completed
                if job.applied
                else RetrainingJobStatus.running
                if elapsed >= STEP_DURATION_SECONDS
                else RetrainingJobStatus.queued
            )
            current_step = None if job.applied else RETRAINING_STEPS[step_index]
            snapshot = DashboardSnapshot.model_validate(self._engine.snapshot) if job.applied else None

            return RetrainingJob(
                job_id=job.job_id,
                status=status,
                started_at=job.started_at,
                completed_at=job.completed_at,
                current_step=current_step,
                snapshot=snapshot,
            )


dashboard_state = DashboardState()
