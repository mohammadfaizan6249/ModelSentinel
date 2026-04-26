export type FeatureStatus = "critical" | "warning" | "stable";
export type TrendDirection = "up" | "flat" | "down";
export type AlertLevel = "critical" | "warning" | "info";
export type GlobalStatus = "critical" | "warning" | "healthy";

export interface FeatureMetric {
  name: string;
  psi: number;
  ks: number;
  status: FeatureStatus;
  trend: TrendDirection;
  baselineDistribution: number[];
  currentDistribution: number[];
  trendSeries: number[];
  lastUpdatedAt: string;
}

export interface AlertItem {
  id: string;
  level: AlertLevel;
  feature: string;
  message: string;
  timeAgo: string;
}

export interface DashboardSnapshot {
  modelName: string;
  environment: string;
  features: FeatureMetric[];
  alerts: AlertItem[];
  monitoredFeaturesDelta: string;
  baselineAccuracy: number;
  currentAccuracy: number;
  validationAccuracy: number;
  healthPercent: number;
  healthDeltaText: string;
  lastUpdatedAt: string;
}

export interface SummaryMetrics {
  featureCount: number;
  criticalCount: number;
  warningCount: number;
  avgPsi: number;
  healthPercent: number;
  healthDeltaText: string;
  globalStatus: GlobalStatus;
}

export interface AiAnalysisResult {
  generatedAt: string;
  sections: Array<{
    title: string;
    body: string;
  }>;
  note: string;
}

export interface RetrainProgress {
  progress: number;
  label: string;
}

export type RetrainingJobStatus = "queued" | "running" | "completed";

export interface RetrainingJob {
  jobId: string;
  status: RetrainingJobStatus;
  startedAt: string;
  currentStep: RetrainProgress | null;
  completedAt?: string | null;
  snapshot?: DashboardSnapshot | null;
}
