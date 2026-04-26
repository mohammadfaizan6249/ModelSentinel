import type { DashboardSnapshot, FeatureMetric, RetrainProgress } from "../types";
import {
  createAlerts,
  getFeatureStatus,
  getTrendDirection
} from "../lib/dashboard";

const baselineDistributions: Record<string, number[]> = {
  credit_score: [0.05, 0.08, 0.12, 0.18, 0.22, 0.15, 0.1, 0.06, 0.03, 0.01],
  income: [0.12, 0.18, 0.2, 0.16, 0.13, 0.09, 0.06, 0.04, 0.01, 0.01],
  debt_ratio: [0.08, 0.15, 0.2, 0.18, 0.14, 0.1, 0.07, 0.05, 0.02, 0.01],
  loan_amount: [0.1, 0.15, 0.18, 0.17, 0.14, 0.11, 0.08, 0.04, 0.02, 0.01],
  employment_yrs: [0.2, 0.22, 0.18, 0.15, 0.1, 0.07, 0.04, 0.02, 0.01, 0.01],
  age: [0.08, 0.14, 0.18, 0.2, 0.16, 0.12, 0.07, 0.03, 0.01, 0.01]
};

const baseFeatureSeeds = [
  { name: "credit_score", psi: 0.31, ks: 0.28 },
  { name: "income", psi: 0.19, ks: 0.15 },
  { name: "debt_ratio", psi: 0.13, ks: 0.1 },
  { name: "loan_amount", psi: 0.06, ks: 0.05 },
  { name: "employment_yrs", psi: 0.04, ks: 0.04 },
  { name: "age", psi: 0.02, ks: 0.02 }
];

export const retrainingSteps: RetrainProgress[] = [
  { progress: 10, label: "Loading 90 days of production training data..." },
  { progress: 24, label: "Validating schema and preprocessing features..." },
  { progress: 44, label: "Training fold 1/3 on refreshed population..." },
  { progress: 63, label: "Training fold 2/3 on refreshed population..." },
  { progress: 82, label: "Training fold 3/3 and evaluating holdout..." },
  { progress: 94, label: "Registering CreditRisk_v2.2 candidate..." },
  { progress: 100, label: "Deploy complete. New reference window is active." }
];

function normalize(values: number[]): number[] {
  const total = values.reduce((sum, value) => sum + value, 0);
  return values.map((value) => Number((value / total).toFixed(4)));
}

function buildCurrentDistribution(base: number[], psi: number): number[] {
  const intensity = psi * 0.24;
  return normalize(
    base.map((value, index) => {
      const direction = index < 4 ? -1 : 1;
      const variation = 0.75 + Math.random() * 0.5;
      return Math.max(0.004, value + direction * intensity * variation);
    })
  );
}

function buildTrendSeries(finalPsi: number): number[] {
  const points = Array.from({ length: 24 }, (_, index) => {
    const progress = index / 23;
    const baseline = finalPsi * (0.32 + 0.68 * Math.pow(progress, 1.4));
    const jitter = (Math.random() - 0.5) * 0.016;
    return Number(Math.max(0.01, baseline + jitter).toFixed(3));
  });
  points[points.length - 1] = Number(finalPsi.toFixed(3));
  return points;
}

export function createFeatureMetrics(): FeatureMetric[] {
  return baseFeatureSeeds.map((seed, index) => {
    const status = getFeatureStatus(seed.psi);
    const previousPsi =
      index % 3 === 0 ? seed.psi - 0.018 : index % 2 === 0 ? seed.psi : seed.psi + 0.004;

    return {
      name: seed.name,
      psi: seed.psi,
      ks: seed.ks,
      status,
      trend: getTrendDirection(seed.psi - previousPsi),
      baselineDistribution: baselineDistributions[seed.name],
      currentDistribution: buildCurrentDistribution(
        baselineDistributions[seed.name],
        seed.psi
      ),
      trendSeries: buildTrendSeries(seed.psi),
      lastUpdatedAt: new Date().toISOString()
    };
  });
}

export function createDashboardSnapshot(): DashboardSnapshot {
  const features = createFeatureMetrics();
  return {
    modelName: "CreditRisk_v2.1",
    environment: "prod-us-east",
    features,
    alerts: createAlerts(features),
    monitoredFeaturesDelta: "+2 this week",
    baselineAccuracy: 0.741,
    currentAccuracy: 0.681,
    validationAccuracy: 0.733,
    healthPercent: 92,
    healthDeltaText: "accuracy drop: -6.0%",
    lastUpdatedAt: new Date().toISOString()
  };
}
