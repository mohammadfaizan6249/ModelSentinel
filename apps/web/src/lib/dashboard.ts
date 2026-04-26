import type {
  AiAnalysisResult,
  AlertItem,
  FeatureMetric,
  GlobalStatus,
  SummaryMetrics,
  TrendDirection
} from "../types";

export const PSI_WARNING_THRESHOLD = 0.1;
export const PSI_CRITICAL_THRESHOLD = 0.25;

export function getFeatureStatus(psi: number): FeatureMetric["status"] {
  if (psi > PSI_CRITICAL_THRESHOLD) {
    return "critical";
  }
  if (psi > PSI_WARNING_THRESHOLD) {
    return "warning";
  }
  return "stable";
}

export function getTrendDirection(delta: number): TrendDirection {
  if (delta > 0.004) {
    return "up";
  }
  if (delta < -0.004) {
    return "down";
  }
  return "flat";
}

export function trendSymbol(trend: TrendDirection): string {
  if (trend === "up") {
    return "↑";
  }
  if (trend === "down") {
    return "↓";
  }
  return "→";
}

export function formatClock(timestamp: string): string {
  return new Date(timestamp).toLocaleTimeString("en-US", {
    hour12: false
  });
}

export function formatAnalysisTime(timestamp: string): string {
  return new Date(timestamp).toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit"
  });
}

export function createAlerts(features: FeatureMetric[]): AlertItem[] {
  const sorted = [...features].sort((left, right) => right.psi - left.psi);
  return sorted
    .filter((feature) => feature.status !== "stable")
    .slice(0, 4)
    .map((feature, index) => {
      const baseMessage =
        feature.status === "critical"
          ? `PSI exceeded the critical threshold (${feature.psi.toFixed(2)} > ${PSI_CRITICAL_THRESHOLD.toFixed(2)}). Distribution mass is shifting enough to threaten score calibration.`
          : `Moderate drift detected with PSI ${feature.psi.toFixed(2)}. Feature movement is large enough to merit validation before silent performance erosion compounds.`;
      const detail =
        feature.name === "credit_score"
          ? "Lower-score segments are over-represented versus baseline, which can bias approvals and risk ranking."
          : feature.name === "income"
            ? "Median applicant earnings appear to be moving down, which may reflect a new customer mix or upstream data mapping drift."
            : feature.name === "debt_ratio"
              ? "Debt burden is creeping up across recent applicants, increasing the chance of underestimating default exposure."
              : "The current production slice is diverging from the training reference window.";

      return {
        id: `${feature.name}-${index}`,
        level: feature.status === "critical" ? "critical" : "warning",
        feature: feature.name,
        message: `${baseMessage} ${detail}`,
        timeAgo: `${14 + index * 22} mins ago`
      };
    });
}

export function calculateSummary(features: FeatureMetric[]): SummaryMetrics {
  const featureCount = features.length;
  const criticalCount = features.filter(
    (feature) => feature.status === "critical"
  ).length;
  const warningCount = features.filter(
    (feature) => feature.status === "warning"
  ).length;
  const avgPsi =
    features.reduce((total, feature) => total + feature.psi, 0) / featureCount;
  const healthPercent = Math.max(
    18,
    Math.round(100 - criticalCount * 24 - warningCount * 11 - avgPsi * 34)
  );

  let globalStatus: GlobalStatus = "healthy";
  if (criticalCount > 0) {
    globalStatus = "critical";
  } else if (warningCount > 0) {
    globalStatus = "warning";
  }

  return {
    featureCount,
    criticalCount,
    warningCount,
    avgPsi,
    healthPercent,
    healthDeltaText:
      globalStatus === "critical"
        ? "accuracy drop: -8.3%"
        : globalStatus === "warning"
          ? "accuracy drop: -3.4%"
          : "accuracy stable: +0.6%",
    globalStatus
  };
}

export function calculateSummaryFromSnapshot(
  featureCount: number,
  criticalCount: number,
  warningCount: number,
  avgPsi: number,
  healthPercent: number,
  healthDeltaText: string
): SummaryMetrics {
  let globalStatus: GlobalStatus = "healthy";
  if (criticalCount > 0) {
    globalStatus = "critical";
  } else if (warningCount > 0) {
    globalStatus = "warning";
  }

  return {
    featureCount,
    criticalCount,
    warningCount,
    avgPsi,
    healthPercent,
    healthDeltaText,
    globalStatus
  };
}

export function generateAiAnalysis(
  features: FeatureMetric[],
  summary: SummaryMetrics
): AiAnalysisResult {
  const ordered = [...features].sort((left, right) => right.psi - left.psi);
  const topFeature = ordered[0];
  const secondFeature = ordered[1];
  const drifted = ordered.filter((feature) => feature.status !== "stable");

  return {
    generatedAt: new Date().toISOString(),
    note:
      "Phase 1 uses a deterministic mock analysis. In Phase 2 we can move this behind the backend and connect a real LLM safely.",
    sections: [
      {
        title: "Root Cause Analysis",
        body: `${topFeature.name} is the dominant drift driver with PSI ${topFeature.psi.toFixed(2)} and KS ${topFeature.ks.toFixed(2)}. The joint pattern with ${secondFeature.name} suggests either a customer-segment shift in production traffic or an upstream feature transformation mismatch rather than pure random noise.`
      },
      {
        title: "Business Impact",
        body: `${drifted.length} materially shifted features can distort score calibration and ranking consistency, especially for borderline approvals. With model health at ${summary.healthPercent}%, the most likely failure mode is underestimating risk for applicants whose current distributions are now outside the original training envelope.`
      },
      {
        title: "Immediate Actions",
        body: "Validate the raw source values for the top two drifted features, compare current production cohorts against the training reference window, and run a shadow evaluation on the most recent batch. Freeze any threshold changes until you confirm whether the drift is economic behavior, data quality, or segment mix."
      },
      {
        title: "Long-Term Fixes",
        body: "Persist daily baseline snapshots, add automated data-quality assertions before scoring, and define retraining triggers that combine drift with recent model performance. This reduces false alarms and makes remediation part of an auditable operating process instead of a manual reaction."
      }
    ]
  };
}
