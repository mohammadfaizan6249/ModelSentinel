import { trendSymbol } from "../lib/dashboard";
import type { FeatureMetric } from "../types";

interface FeatureTableProps {
  features: FeatureMetric[];
  selectedIndex: number;
  onSelect: (index: number) => void;
}

export function FeatureTable({
  features,
  selectedIndex,
  onSelect
}: FeatureTableProps) {
  return (
    <section className="panel">
      <div className="panel-header">
        <span className="panel-title">Feature Drift Monitor</span>
        <span className="panel-hint">Click row to inspect</span>
      </div>

      <table className="feat-table">
        <thead>
          <tr>
            <th>Feature</th>
            <th>PSI Score</th>
            <th>KS Stat</th>
            <th>Status</th>
            <th>Trend</th>
          </tr>
        </thead>
        <tbody>
          {features.map((feature, index) => {
            const trend = trendSymbol(feature.trend);
            const trendClass =
              feature.trend === "up"
                ? "trend-critical"
                : feature.trend === "down"
                  ? "trend-stable"
                  : "trend-flat";

            return (
              <tr
                key={feature.name}
                className={`feat-row ${index === selectedIndex ? "selected" : ""}`}
                onClick={() => onSelect(index)}
              >
                <td className="feat-name">{feature.name}</td>
                <td>
                  <div className="psi-stack">
                    <span className={`psi-val ${feature.status}`}>
                      {feature.psi.toFixed(2)}
                    </span>
                    <div className="psi-bar-bg">
                      <div
                        className={`psi-bar-fill ${feature.status}`}
                        style={{
                          width: `${Math.min(100, (feature.psi / 0.4) * 100)}%`
                        }}
                      />
                    </div>
                  </div>
                </td>
                <td className="ks-val">{feature.ks.toFixed(2)}</td>
                <td>
                  <span className={`status-badge ${feature.status}`}>
                    {feature.status}
                  </span>
                </td>
                <td className={`trend-arrow ${trendClass}`}>{trend}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </section>
  );
}
