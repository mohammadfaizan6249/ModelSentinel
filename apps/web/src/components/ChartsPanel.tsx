import { DistributionChart } from "../charts/DistributionChart";
import { PsiTrendChart } from "../charts/PsiTrendChart";
import type { FeatureMetric } from "../types";

interface ChartsPanelProps {
  feature: FeatureMetric;
}

export function ChartsPanel({ feature }: ChartsPanelProps) {
  return (
    <section className="panel">
      <div className="panel-header">
        <span className="panel-title">
          {feature.name} — Distribution Comparison
        </span>
        <span className="panel-hint">
          PSI: {feature.psi.toFixed(2)} · KS: {feature.ks.toFixed(2)}
        </span>
      </div>

      <div className="chart-wrap">
        <div className="chart-label">
          Baseline (blue) vs Current Production (red) · 10 bins
        </div>
        <DistributionChart
          baseline={feature.baselineDistribution}
          current={feature.currentDistribution}
        />
      </div>

      <div className="chart-divider">
        <div className="chart-wrap chart-wrap-secondary">
          <div className="chart-label">PSI Drift Score — last 24h</div>
          <PsiTrendChart status={feature.status} series={feature.trendSeries} />
        </div>
      </div>
    </section>
  );
}
