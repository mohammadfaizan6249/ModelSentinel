from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict


def to_camel(value: str) -> str:
    head, *tail = value.split("_")
    return head + "".join(part.capitalize() for part in tail)


class ApiModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class FeatureStatus(str, Enum):
    critical = "critical"
    warning = "warning"
    stable = "stable"


class TrendDirection(str, Enum):
    up = "up"
    flat = "flat"
    down = "down"


class AlertLevel(str, Enum):
    critical = "critical"
    warning = "warning"
    info = "info"


class GlobalStatus(str, Enum):
    critical = "critical"
    warning = "warning"
    healthy = "healthy"


class RetrainingJobStatus(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"


class FeatureMetric(ApiModel):
    name: str
    psi: float
    ks: float
    status: FeatureStatus
    trend: TrendDirection
    baseline_distribution: list[float]
    current_distribution: list[float]
    trend_series: list[float]
    last_updated_at: datetime


class AlertItem(ApiModel):
    id: str
    level: AlertLevel
    feature: str
    message: str
    time_ago: str


class DashboardSnapshot(ApiModel):
    model_name: str
    environment: str
    features: list[FeatureMetric]
    alerts: list[AlertItem]
    monitored_features_delta: str
    baseline_accuracy: float
    current_accuracy: float
    validation_accuracy: float
    health_percent: int
    health_delta_text: str
    last_updated_at: datetime


class FeatureDistribution(ApiModel):
    feature_name: str
    baseline_distribution: list[float]
    current_distribution: list[float]
    last_updated_at: datetime


class FeatureTrend(ApiModel):
    feature_name: str
    psi_threshold_warning: float
    psi_threshold_critical: float
    series: list[float]
    last_updated_at: datetime


class AiAnalysisSection(ApiModel):
    title: str
    body: str


class AiAnalysisResult(ApiModel):
    generated_at: datetime
    note: str
    sections: list[AiAnalysisSection]


class HealthResponse(ApiModel):
    status: str
    service: str
    version: str


class RetrainingProgress(ApiModel):
    progress: int
    label: str


class RetrainingJob(ApiModel):
    job_id: str
    status: RetrainingJobStatus
    started_at: datetime
    current_step: Optional[RetrainingProgress]
    completed_at: Optional[datetime] = None
    snapshot: Optional[DashboardSnapshot] = None
