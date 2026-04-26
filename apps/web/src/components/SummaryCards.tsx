import type { SummaryMetrics } from "../types";

interface SummaryCardsProps {
  summary: SummaryMetrics;
  monitoredFeaturesDelta: string;
}

export function SummaryCards({
  summary,
  monitoredFeaturesDelta
}: SummaryCardsProps) {
  const alertSeverityClass =
    summary.criticalCount > 0 ? "red" : summary.warningCount > 0 ? "amber" : "green";
  const healthClass =
    summary.globalStatus === "critical"
      ? "red"
      : summary.globalStatus === "warning"
        ? "amber"
        : "green";

  return (
    <section className="summary-row">
      <article className="summary-card">
        <div className="summary-label">Features Monitored</div>
        <div className="summary-value blue">{summary.featureCount}</div>
        <div className="summary-sub">{monitoredFeaturesDelta}</div>
      </article>

      <article className="summary-card">
        <div className="summary-label">Drift Alerts (24h)</div>
        <div className={`summary-value ${alertSeverityClass}`}>
          {summary.criticalCount + summary.warningCount}
        </div>
        <div className="summary-sub">
          {summary.criticalCount} critical · {summary.warningCount} warning
        </div>
      </article>

      <article className="summary-card">
        <div className="summary-label">Avg PSI Score</div>
        <div className="summary-value amber">{summary.avgPsi.toFixed(2)}</div>
        <div className="summary-sub">threshold: 0.10</div>
      </article>

      <article className="summary-card">
        <div className="summary-label">Model Health</div>
        <div className={`summary-value ${healthClass}`}>{summary.healthPercent}%</div>
        <div className="summary-sub">{summary.healthDeltaText}</div>
      </article>
    </section>
  );
}
