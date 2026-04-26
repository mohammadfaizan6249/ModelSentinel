from fastapi import APIRouter

from app.schemas.dashboard import (
    AiAnalysisResult,
    AlertItem,
    DashboardSnapshot,
    FeatureDistribution,
    FeatureMetric,
    FeatureTrend,
    HealthResponse,
    RetrainingJob,
)
from app.services.dashboard_state import dashboard_state

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok", service="modelsentinel-api", version="0.1.0")


@router.get("/dashboard", response_model=DashboardSnapshot)
def get_dashboard() -> DashboardSnapshot:
    return dashboard_state.get_snapshot()


@router.post("/dashboard/refresh", response_model=DashboardSnapshot)
def refresh_dashboard() -> DashboardSnapshot:
    return dashboard_state.refresh_snapshot()


@router.post("/dashboard/live-tick", response_model=DashboardSnapshot)
def live_tick() -> DashboardSnapshot:
    return dashboard_state.live_tick()


@router.get("/features", response_model=list[FeatureMetric])
def list_features() -> list[FeatureMetric]:
    return dashboard_state.get_features()


@router.get("/alerts", response_model=list[AlertItem])
def list_alerts() -> list[AlertItem]:
    return dashboard_state.get_alerts()


@router.get("/features/{feature_name}/distribution", response_model=FeatureDistribution)
def get_feature_distribution(feature_name: str) -> FeatureDistribution:
    return dashboard_state.get_distribution(feature_name)


@router.get("/features/{feature_name}/trend", response_model=FeatureTrend)
def get_feature_trend(feature_name: str) -> FeatureTrend:
    return dashboard_state.get_trend(feature_name)


@router.post("/analysis", response_model=AiAnalysisResult)
def run_analysis() -> AiAnalysisResult:
    return dashboard_state.create_analysis()


@router.post("/retraining", response_model=RetrainingJob)
def start_retraining() -> RetrainingJob:
    return dashboard_state.start_retraining()


@router.get("/retraining/{job_id}", response_model=RetrainingJob)
def get_retraining_status(job_id: str) -> RetrainingJob:
    return dashboard_state.get_retraining_job(job_id)
